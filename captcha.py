import asyncio
from anticaptchaofficial.turnstileproxyless import turnstileProxyless
from colorama import Fore


WEBSITE_URL = "https://app.nodepay.ai/login"
WEBSITE_KEY = "0x4AAAAAAAx1CyDNL8zOEPe7"
API_KEY = "6b53e789e96a5d330a5473a077c2df33"


class ServiceAnticaptcha:

    def __init__(self, api_key):
        self.api_key = api_key
        self.solver = turnstileProxyless()
        self.solver.set_verbose(1)
        self.solver.set_key(self.api_key)
        self.solver.set_website_url(WEBSITE_URL)
        self.solver.set_website_key(WEBSITE_KEY)
        self.solver.set_action("login") 


    def get_captcha_token(self):
        captcha_token = self.solver.solve_and_return_solution()
        if captcha_token != 0:
            return captcha_token
        else:
            raise Exception(f"{Fore.RED}Ошибка при решении капчи: " + self.solver.error_code)


    async def get_captcha_token_async(self):
        return await asyncio.to_thread(self.get_captcha_token)


    async def solve_captcha(self, email):
        try:
            print(Fore.GREEN + f"{Fore.YELLOW}Решение каптчи для {email}...")
            recaptcha_token = await self.get_captcha_token_async()

            print(Fore.GREEN + f"{Fore.GREEN}Каптча для {email} решена: {recaptcha_token}")
            return recaptcha_token
        except Exception as e:
            print(Fore.RED + f"{Fore.RED}Ошибка при решении каптчи для {email}: {e}")
            return None

