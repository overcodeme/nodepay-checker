import aiofiles
import json
import os
import warnings
from base_client import BaseClient
from captcha import ServiceAnticaptcha, API_KEY
from logger import logger
from exceptions import CloudflareException


ELIGIBLE_ACCS_PATH = 'results/eligible_accs.txt'
NOT_ELIGIBLE_ACCS_PATH = 'results/not_eligible_accs.txt'


warnings.filterwarnings("ignore", category=UserWarning, message="Curlm alread closed!")


class NodepayClient(BaseClient):
    TOKENS_FILE_PATH = 'data/tokens_db.json'

    def __init__(self, email='', password='', proxy='', user_agent='', account_logger=''):
        super().__init__()
        self.email = email
        self.password = password
        self.proxy = proxy
        self.user_agent = user_agent
        self.logger = account_logger


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


    @classmethod
    def load_tokens(cls):
        if os.path.exists(cls.TOKENS_FILE_PATH):
            try:
                with open(cls.TOKENS_FILE_PATH, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {}
        return {}
    

    @classmethod
    def save_tokens(cls, tokens):
        os.makedirs(os.path.dirname(cls.TOKENS_FILE_PATH), exist_ok=True)
        with open(cls.TOKENS_FILE_PATH, 'w') as file:
            json.dump(tokens, file)


    @classmethod
    def get_token(cls, email):
        tokens = cls.load_tokens()
        return tokens[email]


    @classmethod
    def save_token(cls, email, token):
        tokens = cls.load_tokens()
        tokens[email] = token
        cls.save_tokens(tokens)


    def _update_headers(self, token):
        headers = self._auth_headers
        return headers.update({'authorization': f'Bearer {token}'}) or headers


    async def info(self, token):
        response = await self.make_request(
            method='GET',
            url='https://api.nodepay.org/api/earn/info?',
            headers=self._update_headers(token)
        )
        return response["data"]


    async def validate_token(self, token):
        try:
            await self.info(token)
            return True
        except CloudflareException as e:
            self.logger.error(e)
        except Exception as e:
            self.logger.error(e)
            return False


    async def get_auth_token(self):
        saved_token = self.get_token(self.email)

        if saved_token:
            if await self.validate_token(saved_token):
                return saved_token
            
        token = await self.login()
        self.save_token(self.email, token)
        return token


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
        token = await self.get_auth_token()
        headers = self._update_headers(token)

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
            await self.save_to_file(NOT_ELIGIBLE_ACCS_PATH, data)
        else:
            await self.save_to_file(ELIGIBLE_ACCS_PATH, data)
            
        return response['data']
        
