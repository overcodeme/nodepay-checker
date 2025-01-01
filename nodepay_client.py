import uuid
from base_client import BaseClient
from captcha import ServiceAnticaptcha, API_KEY
from exceptions import LoginError


class NodepayClient(BaseClient):
    def __init__(self, email: str = '', password: str = '', proxy: str = '', user_agent: str = ''):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy = proxy
        self.user_agent = user_agent
        self.browser_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.proxy or ''))


    def _auth_headers(self):
        return {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm',
            'priority': 'u=1, i',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'none',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }


    def _ping_headers(self, access_token: str):
        headers = self._auth_headers()
        headers["authorization"] = f"Bearer {access_token}"
        return headers


    async def login(self):
        captcha_token = await ServiceAnticaptcha(API_KEY).solve_captcha(self.email)
        headers = self._auth_headers()

        json_data = {
            'user': self.email,
            'password': self.password,
            'remember_me': True,
            'recaptcha_token': captcha_token
        }

        response = await self.make_request(
            method='POST',
            url='https://api.nodepay.org/api/auth/login',
            headers=headers,
            json_data=json_data
        )

        if not response.get('success', False):
            msg = response.get('msg', 'Unknown login error')
            raise LoginError(msg)
        
        return response['data']['user_info']['uid'], response['data']['token']
