from configparser import ConfigParser


def config(filename: str = "database.ini", section: str = "postgresql") -> dict[str, str]:
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception("Секция {0} не найдена в файле {1}".format(section, filename))

    return db
