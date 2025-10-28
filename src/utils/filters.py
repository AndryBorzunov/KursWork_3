def get_employers(data_hh: list[dict]) -> list[dict]:
    """
    Выделение 10 работодателей с наибольшим числом вакансий
    :param data_hh:
    :return:
    """

    employers_list = []
    employers = []
    for vacancy in data_hh:
        if "employer" in vacancy:
            # print(vacancy["employer"])
            employer = vacancy["employer"]["name"]

            if employer not in employers_list:
                employers_list.append(employer)
                # print(employer)
                if "id" in vacancy["employer"]:
                    employers.append(
                        {"id": vacancy["employer"]["id"], "name": vacancy["employer"]["name"], "vacancy_count": 1}
                    )
                else:
                    employers.append({"id": 0, "name": vacancy["employer"]["name"], "vacancy_count": 1})
            else:
                index = employers_list.index(employer)
                employer_dict = employers[index]
                employer_dict["vacancy_count"] += 1
                employers[index] = employer_dict
                # print(employer_dict)

    # print(employers_list)

    return employers


def sort_employers(employers: list[dict]) -> list[dict]:
    """
    Сортировка по количеству вакансий (по убыванию)
    """

    employers.sort(key=lambda x: x["vacancy_count"], reverse=True)
    return employers


def get_top_employers(employers: list[dict], top_n: int) -> list[dict]:
    """
    Выборка нескольких топовых, по количеству вакансий, компаний
    """

    top_employers = []
    for index, item in enumerate(employers):
        if index < top_n:
            top_employers.append(item)
        else:
            break

    return top_employers
