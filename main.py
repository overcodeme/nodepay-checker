import asyncio
import json
import httpx
from colorama import Fore, init
from captcha import ServiceAnticaptcha 


API_KEY = "6b53e789e96a5d330a5473a077c2df33"
ACCOUNTS = "data/accounts.txt"
PROXIES = "data/proxies.txt"
LOGIN_URL = "https://api.nodepay.org/api/auth/login?"
AIRDROP_URL = "https://api.nodepay.org/api/season/airdrop-status?"


HEADERS = {
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


init(autoreset=True)


def load_accounts():
    try:
        with open(ACCOUNTS, "r") as f:
            accounts = [{"email": line.split(":")[0], "password": line.split(":")[1].strip()} for line in f.readlines()]
        if not accounts:
            raise ValueError("Файл с аккаунтами пуст!")
        return accounts
    except FileNotFoundError:
        raise FileNotFoundError(f"Не удалось найти файл с аккаунтами по пути {ACCOUNTS}.")
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Ошибка при загрузке аккаунтов: {e}")


async def login(login_url, account, recaptcha_token):
    try:
        payload = {
            "email": account["email"],
            "password": account["password"],
            "recaptcha_token": recaptcha_token
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(login_url, json=payload, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

        if 'np_token' not in data:
            raise ValueError(f"Не удалось получить np_token для аккаунта {account['email']}")
        
        return data["np_token"]
    except httpx.HTTPStatusError as e:
        raise Exception(f"Ошибка HTTP при авторизации для {account['email']}: {e}")
    except httpx.RequestError as e:
        raise Exception(f"Ошибка запроса при авторизации для {account['email']}: {e}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Ошибка при авторизации для {account['email']}: {e}")


async def get_airdrop_stat(airdrop_url, np_token):
    try:
        headers = {**HEADERS, "Authorization": f"Bearer {np_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(airdrop_url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"Ошибка HTTP при получении статистики аирдропа: {e}")
    except httpx.RequestError as e:
        raise Exception(f"Ошибка запроса при получении статистики аирдропа: {e}")
    except Exception as e:
        raise Exception(f"Ошибка при получении статистики аирдропа: {e}")

async def save_airdrop_stat(account_email, airdrop_data):
    try:
        filename = f"data/{account_email}_airdrop_stat.json"
        with open(filename, 'w') as f:
            json.dump(airdrop_data, f, indent=4)
    except Exception as e:
        raise Exception(f"Ошибка при сохранении статистики аирдропа для {account_email}: {e}")


async def process_account(account, solver):
    print(Fore.CYAN + f"\nОбрабатываем аккаунт: {account['email']}")
    
    try:
        print(Fore.GREEN + "Решение каптчи...")
        recaptcha_token = await solver.solve_captcha()
        print(Fore.GREEN + f"Каптча для {account['email']} решена!")

        print(Fore.GREEN + "Авторизация...")
        np_token = await login(LOGIN_URL, account, recaptcha_token)
        print(Fore.GREEN + f"Авторизация для {account['email']} выполнена успешно!")

        print(Fore.GREEN + "Получение статистики по аирдропу...")
        airdrop_data = await get_airdrop_stat(AIRDROP_URL, np_token)
        print(Fore.GREEN + f"Airdrop статистика для {account['email']} получена!")

        await save_airdrop_stat(account["email"], airdrop_data)
        print(Fore.GREEN + f"Статистика по аирдропу для {account['email']} сохранена в файл.")

    except Exception as e:
        print(Fore.RED + f"Ошибка для {account['email']}: {e}")


async def main():
    try:
        accounts = load_accounts()
        if len(accounts) == 0:
            raise ValueError("Не загружено ни одного аккаунта.")

        print(Fore.GREEN + f"Загружено {len(accounts)} аккаунтов.")
        solver = ServiceAnticaptcha(API_KEY)  # Используем новый решатель каптчи

        tasks = []
        for account in accounts:
            tasks.append(process_account(account, solver))

        await asyncio.gather(*tasks)

    except Exception as e:
        print(Fore.RED + f"Ошибка при обработке аккаунтов: {e}")

if __name__ == "__main__":
    asyncio.run(main())

