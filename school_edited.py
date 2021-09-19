# This file is edited version of
# https://github.com/Team-IF/comcigan-py/blob/master/comcigan/async_school.py.
# Thank you, Team-IF!


from base64 import b64encode
from json import loads

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from reg import (
    reg_daydata,
    reg_prefix,
    reg_route,
    reg_sbname,
    reg_thname,
    extract_int,
    search_reg,
)


class SchoolEdited:
    __slots__ = ("school_code", "_timeurl", "_week_data", "CONSTANTS")

    @classmethod
    async def init(cls, name: str):
        response = cls()

        CONSTANTS = _Constant()

        await CONSTANTS.refresh()

        PREFIX = CONSTANTS.PREFIX
        BASEURL = CONSTANTS.BASEURL
        SEARCHURL = CONSTANTS.SEARCHURL

        response.CONSTANTS = CONSTANTS

        school_search = await _async_request(
            SEARCHURL
            + "%".join(
                str(name.encode("EUC-KR"))
                .upper()[2:-1]
                .replace("\\X", "\\")
                .split("\\")
            )
        )
        school_list: list = loads(school_search.replace("\0", ""))["학교검색"]

        if len(school_list):
            response.school_code = school_list[0][3]

        else:
            raise NameError("No schools have been searched by the name passed.")

        response._timeurl = f"{BASEURL}?" + b64encode(
            f"{PREFIX}{str(response.school_code)}_0_1".encode("UTF-8")
        ).decode("UTF-8")
        response._week_data = [[[[("", "", "")]]]]

        await response.refresh()

        return response

    async def refresh(self):
        request = await _async_request(self._timeurl)
        timetable: dict = loads(request.replace("\0", ""))

        DAYNUM = self.CONSTANTS.DAYNUM
        SBNUM = self.CONSTANTS.SBNUM
        THNUM = self.CONSTANTS.THNUM

        subjects: list = timetable[f"자료{SBNUM}"]
        subjects_long: list = timetable[f"긴자료{SBNUM}"]
        teachers: list = timetable[f"자료{THNUM}"]

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
                        for x in filter(lambda x: str(x)[:-2], _trim(day[1:]))
                    ]
                    for day in class_[1:6]
                ]
                for class_ in grade
            ]
            for grade in timetable[f"자료{DAYNUM}"][1:]
        ]

    def __getitem__(self, item: int) -> list:
        return self._week_data[item - 1]

    def __iter__(self):
        return iter(self._week_data)


_URL = "http://112.186.146.81:4082"


class _Constant:
    __slots__ = ("PREFIX", "DAYNUM", "SBNUM", "THNUM", "BASEURL", "SEARCHURL")

    async def refresh(self):
        request = await _async_request(f"{_URL}/st")

        soup = BeautifulSoup(request, "lxml")
        script: str = soup.find_all("script")[1].contents[0]

        ROUTE = search_reg(reg_route, script)

        self.PREFIX = search_reg(reg_prefix, script)[1:-1]

        self.DAYNUM = extract_int(search_reg(reg_daydata, script))
        self.SBNUM = extract_int(search_reg(reg_sbname, script))
        self.THNUM = extract_int(search_reg(reg_thname, script))

        self.BASEURL = f"{_URL}{ROUTE[1:8]}"
        self.SEARCHURL = f"{self.BASEURL}{ROUTE[8:]}"


async def _async_request(url: str, encoding: str = None):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.text(encoding)


def _trim(list_):
    while list_ and not list_[-1]:
        del list_[-1]
    return list_
