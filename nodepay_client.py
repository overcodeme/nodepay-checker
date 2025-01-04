from base_client import BaseClient
from captcha import ServiceAnticaptcha, API_KEY
from logger import logger


ELIGIBLE_ACCS_PATH = 'results/eligible_accs.txt'
NOT_ELIGIBLE_ACCS_PATH = 'results/not_eligible_accs.txt'


class NodepayClient(BaseClient):

    def __init__(self, email='', password='', proxy='', user_agent='', account_logger=''):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy = proxy
        self.user_agent = user_agent
        self.logger = account_logger


    def save_to_file(self, file_path, data):
        try:
            with open(file_path, 'a') as file:
                file.write(data + '\n')
        except Exception as e:
            self.logger.error('ERROR', f'Error while writting data in the file: {e}')


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
        captcha_token = await ServiceAnticaptcha(API_KEY, account_logger=logger.bind(account=self.email)).solve_captcha()
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
            email=self.email,
            account_logger=self.logger
        )

        if not response.get('success', False):
            msg = response.get('msg', 'Unknown login error')
            self.logger.error(msg)
        
        self.logger.success('Successfully logged in')
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
            self.logger.error(msg)

        if response['data']['is_eligible'] == False:
            self.logger.info('Account not eligible')
        else:
            self.logger.info('Account is eligible')

        data = f'{self.email}:{self.password}'

        if response['data']['is_eligible'] == False:
            self.save_to_file(NOT_ELIGIBLE_ACCS_PATH, data)
        else:
            self.save_to_file(ELIGIBLE_ACCS_PATH, data)
            
        return response['data']
        
