import asyncio
from nodepay_client import NodepayClient
import platform
from fake_useragent import UserAgent


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def load_data(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]
    

async def process_account(account, proxy):
    email, password = account.split(':')
    ua = UserAgent()
    user_agent = ua.random

    async with NodepayClient(email=email, password=password, proxy=proxy, user_agent=user_agent) as client:
        try:
            data = await client.get_airdrop_stats()
            print(f'| — {email} | Account stats: {data}')
        except Exception as e:
            print(f'| — {email} | Error while processing account: {e}')


async def main():
    accounts = load_data('data/accounts.txt')
    proxies = load_data('data/proxies.txt')
    print(f'Uploaded accounts: {len(accounts)}')

    tasks = []
    for account, proxy in zip(accounts, proxies):
        tasks.append(process_account(account, proxy))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())