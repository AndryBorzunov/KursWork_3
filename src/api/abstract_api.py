from abc import ABC, abstractmethod
from typing import Any


class AbstractAPI(ABC):
    """Абстрактный класс для работы с API платформ с вакансиями"""

    @abstractmethod
    def _connect_to_api(self, query_parameters: dict[str, Any]) -> dict | Any | None:
        """Подключение к API"""
        pass

    @abstractmethod
    def get_vacancies(self, search_query: str, employer_id: str) -> list[dict] | None:
        """Получение вакансий по поисковому запросу"""
        pass
