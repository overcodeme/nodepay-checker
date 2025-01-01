import asyncio
import httpx


WEBSITE_URL = "https://app.nodepay.ai/login"
WEBSITE_KEY = "0x4AAAAAAAx1CyDNL8zOEPe7"
API_URL = "https://api.capsolver.com"


class CapSolver:
    def __init__(self, api_key):
        self.api_key = api_key


    async def create_task(self):
        task_payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "CloudflareTurnstileTask",
                "websiteURL": WEBSITE_URL,
                "websiteKey": WEBSITE_KEY
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/createTask", json=task_payload)
            data = response.json()

        if data.get("errorId") != 0:
            raise Exception(f"Ошибка создания задачи: {data.get('errorDescription')}")

        return data["taskId"]


    async def get_task_result(self, task_id):
        while True:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{API_URL}/getTaskResult", json={
                    "clientKey": self.api_key,
                    "taskId": task_id
                })
                data = response.json()

            if data.get("errorId") != 0:
                raise Exception(f"Ошибка получения результата: {data.get('errorDescription')}")

            if data["status"] == "ready":
                return data["solution"]["token"]

            await asyncio.sleep(5)


    async def solve_captcha(self):
        task_id = await self.create_task()
        return await self.get_task_result(task_id)
