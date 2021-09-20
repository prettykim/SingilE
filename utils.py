import re
from datetime import date, timedelta

import aiosqlite
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from school_edited import SchoolEdited


async def edit_info(payload: dict):
    user = _Sql(payload)

    return await user.edit_sql_data()


async def get_cafeteria(number: int):
    parser = _Parser(number)

    return await parser.get_cafeteria()


async def get_timetable(number: int, payload: dict):
    school = await SchoolEdited.init("신길중학교")

    parser = _Parser(number)
    user = _Sql(payload)

    try:
        grade, class_ = await user.get_sql_data()

    except _NoData:
        response = _NoData().response

    else:
        response = parser.get_timetable(school, grade, class_)

    return response


class _NoData(Exception):
    @property
    def response(self):
        return _return_response(
            """누락된 설정이 있어요.
신길이 이용을 위해서 학년과 반 정보를 설정해 주세요.

<명령어>
오늘시간표, 내일시간표, 모레시간표, 정보설정, 도움말"""
        )  # XXX: Is this the best way?


class _Parser:
    def __init__(self, number: int):
        self.number = number

        self.day = str((date.today() + timedelta(days=number)).day)
        self.date_ = (
            "오늘"
            if number == 0
            else ("내일" if number == 1 else ("모레" if number == 2 else None))
        )

    async def get_cafeteria(self):
        day = "0" + self.day if len(self.day) == 1 else self.day
        month = str((date.today() + timedelta(days=self.number)).month)

        day_and_month = ("0" + month if len(month) == 1 else month) + "." + day

        response_head = [f"<{self.date_}({self.day}일) 급식>"]

        async with ClientSession() as session:
            async with session.get("https://singil.sen.ms.kr/index.do") as request:
                html = await request.text()

        soup = BeautifulSoup(html, "lxml").select_one(
            f".school_menu_info > ul:nth-child({self.number + 1}) > li:nth-child(1) > dl:nth-child(1)"
        )

        if soup.select_one(f"dt:nth-child(1) > a:nth-child(1)").text.endswith(
            day_and_month
        ):
            cafeteria = re.findall(
                "[^ \r\n\t()0-9kcal]+",
                soup.select_one(f"dd:nth-child(2) > p:nth-child(2)").text,
            )

            response_head.extend(cafeteria)

            response = "\n".join(response_head)

        else:
            response = f"{self.date_}({self.day}일) 급식은 없어요."

        return _return_response(response)

    def get_timetable(self, school, grade: int, class_: int):
        weekday = (date.today() + timedelta(days=self.number)).weekday()

        try:
            week_data: list = school[grade][class_][weekday]

        except IndexError:
            response = f"{self.date_}({self.day}일) 시간표는 없어요."

        else:
            if week_data:
                response_head = [f"<{self.date_}({self.day}일) 시간표>"]

                for i, _ in enumerate(week_data):
                    timetable: str = week_data[i][0]

                    response_head.append(f"{i + 1}교시: {timetable}")

                response = "\n".join(response_head)

            else:
                response = f"{self.date_}({self.day}일) 시간표는 없어요."

        return _return_response(response)


class _Payload:
    def __init__(self, payload: dict):
        self.payload = payload

    def extract_grade_and_class(self):
        grade = re.search(
            r"\d", self.payload["action"]["detailParams"]["grade"]["origin"][0]
        ).group()
        class_ = re.search(
            r"\d", self.payload["action"]["detailParams"]["class"]["origin"][0]
        ).group()

        return (int(grade), int(class_))  # XXX: Is this the best way?

    def extract_id(self) -> str:
        return self.payload["userRequest"]["user"]["id"]


class _Sql:
    def __init__(self, payload: dict):
        self.payload = _Payload(payload)

    async def edit_sql_data(self):
        id_ = self.payload.extract_id()
        grade, class_ = self.payload.extract_grade_and_class()

        try:
            _check_grade_and_class(grade, class_)

        except ValueError:
            response = "입력하신 정보는 유효하지 않은 값이예요. 다시 시도해 주세요."

        else:
            async with aiosqlite.connect("db.sqlite3") as db:
                async with db.execute(
                    "SELECT id FROM user WHERE id = ?", (id_,)
                ) as cursor:
                    is_user_info_exist = await cursor.fetchone()

                if is_user_info_exist:
                    await db.execute(
                        "UPDATE user SET grade = ?, class = ? WHERE id = ?",
                        (grade, class_, id_),
                    )

                else:
                    await db.execute(
                        "INSERT INTO user VALUES (?, ?, ?)", (id_, grade, class_)
                    )

                await db.commit()

            response = "입력하신 정보가 성공적으로 반영되었어요."

        return _return_response(response)

    async def get_sql_data(self):
        async with aiosqlite.connect("db.sqlite3") as db:
            async with db.execute(
                "SELECT grade, class FROM user WHERE id = ?",
                (self.payload.extract_id(),),
            ) as cursor:
                grade_and_class: tuple[int, int] = await cursor.fetchone()

        if grade_and_class is None:
            raise _NoData

        grade = grade_and_class[0]
        class_ = grade_and_class[1]

        return (grade, class_)


def _check_grade_and_class(grade: int, class_: int):
    if (
        grade == 0
        or class_ == 0
        or (grade == 1 and class_ > 8)
        or (grade == 2 and class_ > 7)
        or (grade == 3 and class_ > 3)
        or grade > 3
    ):
        raise ValueError


def _return_response(text: str):
    return {"version": "2.0", "template": {"outputs": [{"simpleText": {"text": text}}]}}
