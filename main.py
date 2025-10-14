import src.DBManager
from src.DBManager import DBManager

from src.config import config

if __name__ == "__main__":
    params = config()
    db = DBManager("my_db", params)
