from src.api.hh_api import HeadHunterAPI
from src.config import config
from src.DBManager import DBManager
from src.utils.filters import get_employers, get_top_employers, sort_employers


def print_companies_and_vacancies_count(companies: list[dict]) -> None:
    """
    Вывод на терминал наименования компании и количества вакансий
    """
    print("\n")
    for company in companies:
        print(f"{company['employer']} - {company['count_vacancies']} вакансий")
    print("\n")


def print_vacancies(vacancies: list[dict]) -> None:
    """
    Вывод на терминал вакансий
    """
    print("|    Компания     |        Вакансия           |        Зарплата        |              Ссылка           |")
    for vacancy in vacancies:
        print(f"| {vacancy['employer']} | {vacancy['vacancy']} | {vacancy['salary']} | {vacancy['url']} |")

    print("\n")


def user_interaction() -> None:
    """
    Функция для взаимодействия с пользователем
    """

    platforms = ["HeadHunter"]
    print(f"Платформа для поиска вакансий: {platforms} ")

    # Создание экземпляра класса для работы с API сайтов с вакансиями
    hh_api = HeadHunterAPI()

    search_query = input("Введите поисковый запрос: ")

    # Получение вакансий с hh.ru
    vacancies_json = hh_api.get_vacancies(search_query)

    # Выделяем список работодателей
    employers = get_employers(vacancies_json)

    # Сортируем список работодателей по количеству вакансий
    employers = sort_employers(employers)

    # Получаем список первых 10 работодателей
    employers = get_top_employers(employers, 10)
    print(employers)

    # Получаем список вакансий
    vacancies = []
    for employer in employers:
        vacancies_json = hh_api.get_vacancies(search_query, employer["id"])
        print(f"{employer['id']} - {len(vacancies_json)}")
        for item in vacancies_json:
            vacancies.append(item)

    # работа с БД

    # Считываем параметры. Файл по умолчанию - database.ini
    params = config()

    # Создаём класс DBManager. Загружаем список вакансий в базу данных
    db = DBManager("my_db", params, vacancies)

    # Получаем список компаний и количество вакансий в каждой компании
    employers = db.get_companies_and_vacancies_count()
    print_companies_and_vacancies_count(employers)
    # print(employers)

    # Получаем список всех вакансий
    vacancies = db.get_all_vacancies()
    print("Все вакансии")
    print_vacancies(vacancies)

    # Получаем средний размер зарплаты всех вакансий
    avg = db.get_avg_salary()
    print(f"Средняя зарплата: {avg}")

    # Получаем вакансии с зарплатой выше средней
    vacancies_top = db.get_vacancies_with_higher_salary(avg)
    print("Вакансии с зарплатой выше средней")
    print_vacancies(vacancies_top)

    # Получаем вакансии в наименовании которых есть ключевое слово
    keyword = input("Введите ключевое слово для поиска вакансии: ")
    vacancies_keyword = db.get_vacancies_with_keyword(keyword)
    print(f"Вакансии, в наименовании которых содержится слово {keyword}")
    print_vacancies(vacancies_keyword)


if __name__ == "__main__":
    user_interaction()
