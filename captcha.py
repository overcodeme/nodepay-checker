import asyncio
from anticaptchaofficial.turnstileproxyless import turnstileProxyless
from logger import logger


WEBSITE_URL = 'https://app.nodepay.ai/login'
WEBSITE_KEY = '0x4AAAAAAAx1CyDNL8zOEPe7'
API_KEY = '6b53e789e96a5d330a5473a077c2df33'


class ServiceAnticaptcha:

    def __init__(self, api_key):
        self.api_key = api_key
        self.solver = turnstileProxyless()
        self.solver.set_verbose(1)
        self.solver.set_key(self.api_key)
        self.solver.set_website_url(WEBSITE_URL)
        self.solver.set_website_key(WEBSITE_KEY)
        self.solver.set_action('login') 


    def get_captcha_token(self):
        captcha_token = self.solver.solve_and_return_solution()
        return captcha_token


    async def get_captcha_token_async(self):
        return await asyncio.to_thread(self.get_captcha_token)


    async def solve_captcha(self, email):
        try:
            logger.bind(account=email).error('Solving captcha...')
            recaptcha_token = await self.get_captcha_token_async()

            logger.bind(account=email).success('Captcha solved!')
            return recaptcha_token
        except Exception as e:
            logger.bind(account=email).error(f'Error while solving captcha: {e}')
            return None

