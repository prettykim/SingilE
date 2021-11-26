# This file is edited version of
# https://github.com/Team-IF/comcigan-py/blob/master/comcigan/async_school.py
# Thank you, Team-IF!


from base64 import b64encode
from datetime import date, timedelta
from json import loads

from bs4 import BeautifulSoup

from .utils.constants import (
    COMCIGAN_URL,
    REGEX_DAILY_DATA,
    REGEX_PREFIX,
    REGEX_ROUTE,
    REGEX_SUBJECT,
)
from .utils.exception import NoData
from .utils.functions import extract_int, get, get_info, search, trim


# public interface -----------------------------------------------------
async def get_timetable(when: int, payload: dict):
    day = str((date.today() + timedelta(days=when)).day)
    weekday = (date.today() + timedelta(days=when)).weekday()
    date_ = (
        "오늘" if when == 0 else ("내일" if when == 1 else ("모레" if when == 2 else None))
    )

    josa = "는" if when == 2 else "은"

    if weekday > 4:
        text = f"{date_}({day}일){josa} 휴일이라 시간표가 없네요."

    else:
        try:
            grade, class_ = await get_info(payload)

        except NoData as e:
            text = str(e)

        else:
            week_data = await _Timetable("신길중학교")

            try:
                timetable: list = week_data[grade][class_][weekday]

            except IndexError:
                text = f"{date_}({day}일){josa} 휴일이라 시간표가 없네요."

            else:
                if timetable:
                    header = [f"<{date_}({day}일) 시간표>"]

                    for i, _ in enumerate(timetable):
                        subject: str = timetable[i]

                        header.append(f"{i + 1}교시: {subject}")

                    text = "\n".join(header)

                else:
                    text = f"{date_}({day}일){josa} 휴일이라 시간표가 없네요."

    return text


# internals ------------------------------------------------------------
class _Timetable:
    async def __new__(cls, name: str):
        instance = super().__new__(cls)

        await instance.init(name)

        return instance

    async def init(self, name: str):
        response = await get(f"{COMCIGAN_URL}/st")
        soup = BeautifulSoup(response, "lxml")

        del response  # XXX: Is this necessary?

        script: str = soup.find_all("script")[1].contents[0]

        route = search(REGEX_ROUTE, script)
        PREFIX = search(REGEX_PREFIX, script)[1:-1]

        daily_data_number = extract_int(search(REGEX_DAILY_DATA, script))
        subject_number = extract_int(search(REGEX_SUBJECT, script))

        BASE_URL = f"{COMCIGAN_URL}{route[1:8]}"
        URL = f"{BASE_URL}{route[8:]}"

        response = await get(
            URL
            + "%".join(
                str(name.encode("EUC-KR"))
                .upper()[2:-1]
                .replace("\\X", "\\")
                .split("\\")
            )
        )
        school_list: list = loads(response.replace("\0", ""))["학교검색"]

        del response  # XXX: Is this necessary?

        if school_list:
            school_code: int = school_list[0][3]

        else:
            raise NameError("No schools have been searched by the name passed.")

        final_url = f"{BASE_URL}?" + b64encode(
            f"{PREFIX}{str(school_code)}_0_1".encode("UTF-8")
        ).decode("UTF-8")

        response = await get(final_url)
        raw_timetable: dict = loads(response.replace("\0", ""))

        subjects: list = raw_timetable[f"자료{subject_number}"]

        self.week_data = [
            [
                [
                    [
                        subjects[int(str(i)[-2:])]
                        for i in filter(lambda x: str(x)[:-2], trim(weekday[1:]))
                    ]
                    for weekday in class_[1:6]
                ]
                for class_ in grade
            ]
            for grade in raw_timetable[f"자료{daily_data_number}"][1:]
        ]

    def __getitem__(self, index: int):
        return self.week_data[index - 1]
