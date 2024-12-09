import aiohttp

from config import API_URL


class NetWorkWorker:

    # Функция для отправки модели на сервер
    async def send_model(self, endpoint: str, model_data: dict):
        """
        Отправляет модель на сервер по заданному endpoint.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{API_URL}{endpoint}", json=model_data) as response:
                    if response.status == 200 or response.status == 401:
                        return response
                    else:
                        return None
            except aiohttp.ClientError as e:
                return None

    # Функция для получения списка моделей
    async def get_model_list(self, endpoint: str, params: dict = None):
        """
        Получает список моделей с сервера по заданному endpoint.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{API_URL}{endpoint}", params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
            except aiohttp.ClientError as e:
                return None

    async def get_model_by_params(self, endpoint: str, params: dict):
        """
        Получает одну модель с сервера по заданному endpoint и id модели.
        """
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            try:
                async with session.get(f"{API_URL}{endpoint}", params=params) as response:
                    if response.status == 200:
                        return await response.json()  # возвращаем данные модели
                    else:
                        return None
            except aiohttp.ClientError as e:
                return None

    async def get_table(self, endpoint: str):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            async with session.get(f"{API_URL}{endpoint}") as response:
                return response
