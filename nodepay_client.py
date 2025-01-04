from base_client import BaseClient
from captcha import ServiceAnticaptcha, API_KEY
from logger import logger


ELIGIBLE_ACCS_PATH = 'results/eligible_accs.txt'
NOT_ELIGIBLE_ACCS_PATH = 'results/not_eligible_accs.txt'

class NodepayClient(BaseClient):

    def __init__(self, email='', password='', proxy='', user_agent=''):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy = proxy
        self.user_agent = user_agent


    def save_to_file(self, file_path, data):
        try:
            with open(file_path, 'a') as file:
                file.write(data + '\n')
        except Exception as e:
            logger.log('ERROR', account=self.email, message=f'Error while writting data in the file: {e}')


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
            json_data=json_data,
            email=self.email
        )

        if not response.get('success', False):
            msg = response.get('msg', 'Unknown login error')
            logger.bind(account=self.email).error(msg)
        
        logger.bind(account=self.email).success('Successfully logged in')
        token = response['data']['token']
        return token


    async def get_airdrop_stats(self):
        token = await self.login()

        headers = self._auth_headers()
        headers['authorization'] = f'Bearer {token}'

        response = await self.make_request(
            method='GET',
            url='https://api.nodepay.org/api/season/airdrop-status?',
            headers=headers,
            email=self.email
        )

        if not response.get('success', False):
            msg = response.get('msg', 'Unknown getting airdrop stats error')
            logger.bind(account=self.email).error(msg)

        if response['data']['is_eligible'] == False:
            logger.bind(account=self.email).info('Account not eligible')
        else:
            logger.bind(account=self.email).info('Account is eligible')

        data = f'{self.email}:{self.password}'

        if response['data']['is_eligible'] == False:
            self.save_to_file(NOT_ELIGIBLE_ACCS_PATH, data)
        else:
            self.save_to_file(ELIGIBLE_ACCS_PATH, data)
            
        return response['data']
        
