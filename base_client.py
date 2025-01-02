import json
from curl_cffi.requests import AsyncSession
from exceptions import CloudflareException


class BaseClient:
    def __init__(self):
        self.headers = None
        self.session = None
        self.proxy = None
        self.user_agent = None


    async def create_session(self, proxy=None, user_agent=None):
        self.proxy = proxy
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': 'chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm',
            'priority': 'u=1, i',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'none',
            'user-agent': user_agent,
        }
        if self.session:
            await self.session.close()

        self.session = AsyncSession(
            impersonate='chrome110',
            headers=self.headers,
            # proxies={'http': proxy, 'https': proxy} if proxy else None,
            verify=False
        )


    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None


    async def make_request(self, method, url, headers: dict = None, json_data: dict = None):
        if not self.session:
            await self.create_session(self.proxy, self.user_agent)

        try:
            response = await self.session.request(
                method=method,
                url=url,
                headers=headers or self.headers,
                json=json_data,
                proxy=self.proxy,
                timeout=30,
                impersonate="chrome110"
            )

            if response.status_code in [400, 403]:
                raise CloudflareException('Cloudflare protection detected')

            try:
                response_json = response.json()
            except json.JSONDecodeError:
                raise Exception('Failed to parse JSON response')

            if not response.ok:
                error_msg = response_json.get('error', 'Unknown error')
                raise Exception(f'Request failed with status {response.status_code}: {error_msg}')
            
            return response_json
        except Exception as e:
            raise Exception(f'Request failed: {e}')


    async def __aenter__(self):
        await self.create_session(self.proxy, self.user_agent)
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()

            