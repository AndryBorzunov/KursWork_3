from typing import Any

import requests

from src.api.abstract_api import AbstractAPI


class HeadHunterAPI(AbstractAPI):
    """Класс для получения вакансий через API"""

    __url: str  # Адрес платформы
    __page: int  # Страница запроса
    __found_dict: dict[str, Any]  # Результат запроса

    def __init__(self) -> None:
        """Инициализация переменных"""

        self.__url = "https://api.hh.ru/vacancies"
        self.__page = 0
        self.__found_dict = dict()

    def _connect_to_api(self, query_parameters: dict[str, Any]) -> dict | Any | None:
        """Запрос данных с сервиса"""

        params = query_parameters  # json.loads(query_parameters)
        headers = {"HH-User-Agent": "Kurswork2/1.0 (andry73@yandex.ru)"}

        print(f"Идет поиск вакансий - страница {self.__page}")

        response = requests.get(self.__url, params, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_vacancies(self, search_query: str, employer_id: str = None) -> list[dict] | None:
        """Получение вакансий через API Head Hunter, генерация запросов"""

        # Формируем строку запроса
        self.__page = 0
        query_dict = dict()
        query_dict["text"] = search_query
        if employer_id is not None:
            query_dict["employer_id"] = employer_id  # "3529"
        query_dict["page"] = str(self.__page)
        query_dict["per_page"] = "100"

        # params = 'f{"text": {search_query}, "page": {self.__page}, "per_page": "100"}'

        vacancies: list[dict] = []

        while True:
            query_dict["page"] = str(self.__page)
            response = self._connect_to_api(query_dict)

            if response is None:
                return vacancies

            else:
                counter = 0
                for item in response["items"]:
                    vacancy = dict()
                    vacancy["id"] = item["id"]
                    vacancy["name"] = item["name"]
                    if "professional_roles" in item:
                        vacancy["professional_roles"] = item["professional_roles"]
                    if "salary" in item:
                        vacancy["salary"] = item["salary"]
                    if "area" in item:
                        vacancy["area"] = item["area"]
                    if "employer" in item:
                        vacancy["employer"] = item["employer"]
                    if "employment" in item:
                        vacancy["employment"] = item["employment"]
                    if "created_at" in item:
                        vacancy["created_at"] = item["created_at"]
                    if "archived" in item:
                        vacancy["archived"] = item["archived"]
                    if "work_format" in item:
                        vacancy["work_format"] = item["work_format"]
                    if "published_at" in item:
                        vacancy["published_at"] = item["published_at"]
                    if "apply_alternate_url" in item:
                        vacancy["apply_alternate_url"] = item["apply_alternate_url"]
                    if "snippet" in item:
                        vacancy["snippet"] = item["snippet"]

                    vacancies.append(vacancy)
                    counter += 1

                # break

                if counter == 0:
                    break
                else:
                    self.__page += 1

                self.__found_dict = {
                    "found": response["found"],
                    "page": response["page"],
                    "per_page": response["per_page"],
                }

        return vacancies

    @property
    def found_dict(self) -> dict[str, Any]:
        return self.__found_dict
