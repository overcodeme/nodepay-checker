import uuid
from base_client import BaseClient
from captcha import ServiceAnticaptcha, API_KEY
from exceptions import LoginError, GetAirdropStatsError


class NodepayClient(BaseClient):

    def __init__(self, email='', password='', proxy='', user_agent=''):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy = proxy
        self.user_agent = user_agent
        self.browser_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.proxy or ''))


    def _auth_headers(self):
        return {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'referer': 'https://api.nodepay.org/',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="112", "Google Chrome";v="112"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
        }



    async def login(self):
        captcha_token = await ServiceAnticaptcha(API_KEY).solve_captcha(self.email)
        headers = self._auth_headers()

        json_data = {
            'user': self.email,
            'password': self.password,
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
        
        print(f'| — Account: {self.email} | Successfully logged in | {response['data']['token']}')
        token = response['data']['token']
        return token
    

    async def info(self, access_token):
        headers = self._auth_headers()
        headers['authorization'] = f'Bearer {access_token}'
        response = await self.make_request(
            method='GET',
            url='https://api.nodepay.org/api/earn/info?',
            headers=headers
        )
        return response, headers


    async def get_airdrop_stats(self):
        print(f'| — Account: {self.email} | Getting airdrop stats...')
        token = await self.login()

        headers = self._auth_headers()
        headers['authorization'] = f'Bearer {token}'

        response = await self.make_request(
            method='GET',
            url='https://api.nodepay.org/api/season/airdrop-status?',
            headers=headers
        )

        if not response.get('success', False):
            msg = response.get('msg', 'Unknown getting airdrop stats error')
            raise GetAirdropStatsError(msg)
        print(f'| — Account: {self.email} | Successfully got account stats')
        return response['data']
        
