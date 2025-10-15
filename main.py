import src.DBManager
from src.DBManager import DBManager
import json

from src.config import config

if __name__ == "__main__":

    with open('vacancies.json') as file:
        data = json.load(file)

    params = config()
    db = DBManager("my_db", params, data)

    employers = db.get_companies_and_vacancies_count()
    print(employers)

    vacancies = db.get_all_vacancies()

    avg = db.get_avg_salary()
    print(avg)

    db.get_vacancies_with_higher_salary(avg)
