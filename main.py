import asyncio
from nodepay_client import NodepayClient
from colorama import Fore
import platform


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def load_data(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]
    

async def process_account(account, proxy):
    email, password = account.split(':')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

    async with NodepayClient(email=email, password=password, proxy=proxy, user_agent=user_agent) as client:
        try:
            user_id, access_token = await client.login()
            print(f'{Fore.GREEN}Успешный вход: {email} | User ID: {user_id}')
        except Exception as e:
            print(f'{Fore.RED}Ошибка при обработке аккаунта {email}: {e}')


async def main():
    accounts = load_data('data/accounts.txt')
    proxies = load_data('data/proxies.txt')

    print(f'{Fore.YELLOW}Загружено аккаунтов: {len(accounts)}')

    tasks = []
    for account, proxy in zip(accounts, proxies):
        tasks.append(process_account(account, proxy))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())