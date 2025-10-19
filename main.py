from src.DBManager import DBManager
from src.utils.filters import get_employers, get_top_employers, sort_employers
from src.api.hh_api import HeadHunterAPI
import json

from src.config import config

if __name__ == "__main__":

    with open('vacancies.json') as file:
        data = json.load(file)

    # Создание экземпляра класса для работы с API сайтов с вакансиями
    hh_api = HeadHunterAPI()

    # Получение вакансий с hh.ru в формате JSON
    vacancies_json = hh_api.get_vacancies("python")

    #print(vacancies_json)

    employers = get_employers(vacancies_json)
    #print(employers)

    employers = sort_employers(employers)
    #print(employers)

    employers = get_top_employers(employers, 10)
    print(employers)

    vacancies = []
    for employer in employers:
        vacancies_json = hh_api.get_vacancies("python", employer["id"])
        for item in vacancies_json:
            vacancies.append(item)

    #print(vacancies)

    # работа с БД
    params = config()
    db = DBManager("my_db", params, vacancies)

    employers = db.get_companies_and_vacancies_count()
    print(employers)

    vacancies = db.get_all_vacancies()
    #print(vacancies)

    avg = db.get_avg_salary()
    print(avg)

    vacancies_top = db.get_vacancies_with_higher_salary(avg)
    print(vacancies_top)

    vacancies_keyword = db.get_vacancies_with_keyword("инженер")
    print("инженер")
    print(vacancies_keyword)
