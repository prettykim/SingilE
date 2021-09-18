from base64 import b64encode
from json import loads

from bs4 import BeautifulSoup
from requests import get

from reg import (
    reg_daydata,
    reg_prefix,
    reg_route,
    reg_sbname,
    reg_thname,
    extract_int,
    search_reg,
)


def trim(list_):
    while list_ and not list_[-1]:
        del list_[-1]
    return list_


URL = "http://112.186.146.81:4082"

request = get(f"{URL}/st")
request.encoding = "EUC-KR"

html = BeautifulSoup(request.text, "lxml")
script = html.find_all("script")[1].contents[0]

DAYNUM = extract_int(search_reg(reg_daydata, script))
PREFIX = search_reg(reg_prefix, script)[1:-1]
ROUTE = search_reg(reg_route, script)
SBNUM = extract_int(search_reg(reg_sbname, script))
THNUM = extract_int(search_reg(reg_thname, script))

BASEURL = f"{URL}{ROUTE[1:8]}"
SEARCHURL = f"{BASEURL}{ROUTE[8:]}"


class SchoolEdited:
    __slots__ = ("region", "name", "school_code", "_timeurl", "_week_data")

    def __init__(self, name):
        school_search = get(
            SEARCHURL
            + "%".join(
                str(name.encode("EUC-KR"))
                .upper()[2:-1]
                .replace("\\X", "\\")
                .split("\\")
            )
        )
        school_search.encoding = "UTF-8"
        school_list = loads(school_search.text.replace("\0", ""))["학교검색"]

        if len(school_list):
            self.region = school_list[0][1]
            self.name = school_list[0][2]
            self.school_code = school_list[0][3]

        else:
            raise NameError("No schools have been searched by the name passed.")

        self._timeurl = f"{BASEURL}?" + b64encode(
            f"{PREFIX}{str(self.school_code)}_0_1".encode("UTF-8")
        ).decode("UTF-8")
        self._week_data = [[[[("", "", "")]]]]
        self.refresh()

    def refresh(self):
        timetable_request = get(self._timeurl)
        timetable_request.encoding = "UTF-8"
        timetable = loads(timetable_request.text.replace("\0", ""))

        subjects = timetable[f"자료{SBNUM}"]
        subjects_long = timetable[f"긴자료{SBNUM}"]
        teachers = timetable[f"자료{THNUM}"]

        self._week_data = [
            [
                [
                    [
                        (
                            subjects[int(str(x)[-2:])],
                            subjects_long[int(str(x)[-2:])],
                            ""
                            if int(str(x)[:-2]) >= len(teachers)
                            else teachers[int(str(x)[:-2])],
                        )
                        for x in filter(lambda x: str(x)[:-2], trim(day[1:]))
                    ]
                    for day in class_[1:6]
                ]
                for class_ in grade
            ]
            for grade in timetable[f"자료{DAYNUM}"][1:]
        ]

    def __getitem__(self, item):
        return self._week_data[item - 1]

    def __iter__(self):
        return iter(self._week_data)

    def __repr__(self):
        return f"School('{self.name}')"

    def __str__(self):
        return str(self._week_data)
