import aiohttp

from constance import API_URL


class NetWorkWorker:


    # Функция для отправки модели на сервер
    async def send_model(endpoint: str, model_data: dict):
        """
        Отправляет модель на сервер по заданному endpoint.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{API_URL}{endpoint}", json=model_data) as response:
                    if response.status == 201:
                        return await response.json()  # возвращаем данные из ответа, если запрос успешен
                    else:
                        print(f"Ошибка при отправке модели: {response.status} - {response.reason}")
                        return None
            except aiohttp.ClientError as e:
                print(f"Ошибка сети при отправке модели: {e}")
                return None

    # Функция для получения списка моделей
    async def get_model_list(endpoint: str, params: dict = None):
        """
        Получает список моделей с сервера по заданному endpoint.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{API_URL}{endpoint}", params=params) as response:
                    if response.status == 200:
                        return await response.json()  # возвращаем список моделей
                    else:
                        print(f"Ошибка при получении списка моделей: {response.status} - {response.reason}")
                        return None
            except aiohttp.ClientError as e:
                print(f"Ошибка сети при получении списка моделей: {e}")
                return None

    # Функция для получения одной модели по ID
    async def get_model_by_params(endpoint: str, params: dict):
        """
        Получает одну модель с сервера по заданному endpoint и id модели.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{API_URL}{endpoint}",params=params) as response:
                    if response.status == 200:
                        return await response.json()  # возвращаем данные модели
                    else:
                        print(f"Ошибка при получении модели: {response.status} - {response.reason}")
                        return None
            except aiohttp.ClientError as e:
                print(f"Ошибка сети при получении модели: {e}")
                return None