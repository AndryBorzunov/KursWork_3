import psycopg2
from psycopg2 import Error


class DBManager:

    __connection = None

    def __init__(self, db_name: str, params: dict):

        cur = None
        try:
            self.__connection= psycopg2.connect(dbname='postgres', **params)
            self.__connection.autocommit = True #set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = self.__connection.cursor()
            print("Соединение установлено!")

            #cur.execute(f"DROP DATABASE {db_name}")
            # Создаём БД
            self.__create_db(db_name, self.__connection)
            self.__connection.close()

            # Создаём таблицы
            self.__connection = psycopg2.connect(dbname=db_name, **params)
            self.__create_table_firms(self.__connection)
            self.__create_table_vacancies(self.__connection)

        except(Exception, Error) as error:
            print("Ошибка", error)

        finally:
            if self.__connection:
                cur.close()
                self.__connection.close()


    @classmethod
    def __check_exist_db(cls, db_name, conn):
        """ Проверка наличия БД """

        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            return cur.fetchone() is not None


    @classmethod
    def __check_exist_table(cls, table_name, conn):
        """ Проверка наличия таблицы """

        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (table_name,))
            rows = cur.fetchone()
            print(rows)
            return rows[0] is not None


    @classmethod
    def __create_db(cls, db_name, conn):
        """ Создание БД """

        with conn.cursor() as cur:
            cur.execute(f"SELECT datname FROM pg_database;")  # WHERE datistemplate=false"))
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
    def __create_table_firms(cls, conn):
        """ Создание таблицы"""

        with conn.cursor() as cur:
            # Проверка наличия таблицы
            is_exist = cls.__check_exist_table("firms", conn)
            print(is_exist)
            if not is_exist:
                # Создаём таблицу
                print("Создаём таблицу firms")
                cur.execute("""
                          CREATE TABLE firms (
                          firm_id SERIAL PRIMARY KEY,
                          name VARCHAR(255) NOT NULL
                          )
                      """)
                conn.commit()
            else:
                cur.execute("SELECT * FROM vacancies")
                print(cur.fetchall())


    @classmethod
    def __create_table_vacancies(cls, conn):
        """ Создание таблицы"""

        with conn.cursor() as cur:
            # Проверка наличия таблицы
            is_exist = cls.__check_exist_table("vacancies", conn)
            print(is_exist)
            if not is_exist:
                # Создаём таблицу
                print("Создаём таблицу vacancies")
                cur.execute("""
                      CREATE TABLE vacancies (
                      vacancy_id SERIAL PRIMARY KEY,
                      firm_id INT,
                      name VARCHAR(255) NOT NULL,
                      vacancy_url TEXT
                      FOREIGN KEY (firm_id) REFERENCES firms(firm_id)
                      )
                  """)
                conn.commit()
            else:
                cur.execute("SELECT * FROM vacancies")
                print(cur.fetchall())
