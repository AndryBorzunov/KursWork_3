import psycopg2
from psycopg2 import Error
from psycopg2.extensions import connection, cursor
from typing import Any


class DBManager:

    __params: dict
    __db_name: str

    def __init__(self, db_name: str, params: dict, data: list[dict[str, Any]]) -> None:

        conn: connection = None
        cur: cursor = None
        self.__params = params
        self.__db_name = db_name

        try:
            conn = psycopg2.connect(dbname="postgres", **params)
            conn.autocommit = True  # set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            print("Соединение установлено!")

            cur.execute(f"DROP DATABASE {db_name}")
            # Создаём БД
            self.__create_db(db_name, conn)
            conn.close()

            # Создаём таблицы
            conn = psycopg2.connect(dbname=db_name, **params)
            self.__create_table_employers(conn)
            self.__create_table_vacancies(conn)

            # Заполняем таблицы данными
            self.__save_data_to_database(data, conn)

        except (Exception, Error) as error:
            print("Ошибка", error)

        finally:
            if conn:
                cur.close()
                conn.close()

    @classmethod
    def __check_exist_db(cls, db_name: str, conn: connection) -> bool:
        """Проверка наличия БД"""

        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            return cur.fetchone() is not None

    @classmethod
    def __check_exist_table(cls, table_name: str, conn: connection) -> bool:
        """Проверка наличия таблицы"""

        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (table_name,))
            rows = cur.fetchone()
            print(rows)
            if rows is not None:
                return rows[0] is not None
            else:
                return False

    @classmethod
    def __create_db(cls, db_name: str, conn: connection) -> None:
        """Создание БД"""

        with conn.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database;")  # WHERE datistemplate=false"))
            rows = cur.fetchall()
            print(rows)

            # Проверка наличия БД
            is_exist = cls.__check_exist_db(db_name, conn)
            print(is_exist)
            if not is_exist:
                # Создаём базу данных
                cur.execute(f"CREATE DATABASE {db_name}")

        conn.commit()

    @classmethod
    def __create_table_employers(cls, conn: connection) -> None:
        """Создание таблицы"""

        with conn.cursor() as cur:
            # Проверка наличия таблицы
            is_exist = cls.__check_exist_table("employers", conn)
            print(is_exist)
            if not is_exist:
                # Создаём таблицу
                print("Создаём таблицу employers")
                cur.execute(
                    """
                          CREATE TABLE employers (
                          employer_id SERIAL PRIMARY KEY,
                          name VARCHAR(255) NOT NULL
                          )
                    """
                )
            else:
                cur.execute("SELECT * FROM employers")
                print(cur.fetchall())

        conn.commit()

    @classmethod
    def __create_table_vacancies(cls, conn: connection) -> None:
        """Создание таблицы"""

        with conn.cursor() as cur:
            # Проверка наличия таблицы
            is_exist = cls.__check_exist_table("vacancies", conn)
            print(is_exist)
            if not is_exist:
                # Создаём таблицу
                print("Создаём таблицу vacancies")
                cur.execute(
                    """
                      CREATE TABLE vacancies (
                      vacancy_id SERIAL PRIMARY KEY,
                      employer_id INT,
                      name VARCHAR(255) NOT NULL,
                      salary INT,
                      vacancy_url TEXT,
                      FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
                      )
                    """
                )
                conn.commit()
            else:
                cur.execute("SELECT * FROM vacancies")
                print(cur.fetchall())

    @classmethod
    def __save_data_to_database(cls, data: list[dict[str, Any]], conn: connection):
        """ Сохранение данных в базу данных """

        with conn.cursor() as cur:

            employers = []
            employer_names = []
            for employer in data:
                if 'employer' in employer:

                    firm_name = employer['employer']['name']

                    print(firm_name)
                    if firm_name not in employer_names:

                        cur.execute(
                            """
                            INSERT INTO employers (name)
                            VALUES (%s)
                            RETURNING employer_id
                            """,
                            (firm_name, )
                        )
                        employer_id = cur.fetchone()[0]
                        employers.append({"employer_id": employer_id, "name": firm_name})
                        employer_names.append(firm_name)

            print(employers)

            for employer in employers:
                for vacancy in data:
                    if 'employer' in vacancy:
                        if vacancy['employer']['name'] == employer['name']:
                            cur.execute(
                                """
                                INSERT INTO vacancies (employer_id, name, salary, vacancy_url)
                                VALUES (%s, %s, %s, %s)
                                """,
                                (employer['employer_id'], vacancy['name'], vacancy['salary'], vacancy['url'])
                            )
        conn.commit()

    def get_companies_and_vacancies_count(self) -> list[dict]:
        """
        Получить список всех компаний и количество вакансий
        в каждой компании
        """

        conn = psycopg2.connect(dbname=self.__db_name, **self.__params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT employers.name, COUNT(vacancies.*) FROM employers
                JOIN vacancies USING(employer_id)
                GROUP BY employers.name
                """
            )
            #JOIN vacancies USING(employer_id)
            rows = cur.fetchall()
            print(rows)

            result = []
            for row in rows:
                result.append({'employer': row[0], 'count_vacncies': row[1]})

            return result

    def get_all_vacancies(self):
        """
        Получить список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию
        """

        conn = psycopg2.connect(dbname=self.__db_name, **self.__params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.name, v.salary, v.vacancy_url
                FROM employers as e
                JOIN vacancies as v USING(employer_id)
                """
            )

            rows = cur.fetchall()
            print(rows)

    def get_avg_salary(self) -> int:
        """
        Получить среднюю зарплату по вакансиям
        """

        conn = psycopg2.connect(dbname=self.__db_name, **self.__params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG(salary) FROM vacancies
                """
            )

            return cur.fetchone()[0]

    def get_vacancies_with_higher_salary(self, salary_min):
        """
        Получить список вакансий, у которых зарплата выше среднего
        значения по всем зарплатам
        """

        conn = psycopg2.connect(dbname=self.__db_name, **self.__params)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.name, v.name, v.salary, v.vacancy_url
                FROM employers as e
                JOIN vacancies as v USING(employer_id)
                WHERE v.salary > %s
                """,
                (salary_min, )
            )

            rows = cur.fetchall()
            print(rows)
