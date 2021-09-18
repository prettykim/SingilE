import re
import sqlite3
from datetime import date, timedelta

from bs4 import BeautifulSoup
from requests import get

from school_edited import SchoolEdited


def edit_info(payload):
    user = _User(payload)

    return user.edit_sql_data()


def get_cafeteria(number):
    parser = _Parser(number)

    return parser.get_cafeteria()


def get_timetable(number, payload):
    school = SchoolEdited("신길중학교")

    parser = _Parser(number)
    user = _User(payload)

    try:
        grade, class_ = user.get_sql_data()

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
    def __init__(self, number):
        self.number = number

        self.day = str((date.today() + timedelta(days=number)).day)
        self.date_ = (
            "오늘"
            if number == 0
            else ("내일" if number == 1 else ("모레" if number == 2 else None))
        )

    def get_cafeteria(self):
        day = "0" + self.day if len(self.day) == 1 else self.day
        month = str((date.today() + timedelta(days=self.number)).month)

        day_and_month = ("0" + month if len(month) == 1 else month) + "." + day

        response_head = [f"<{self.date_}({self.day}일) 급식>"]

        request = get("https://singil.sen.ms.kr/index.do")
        html = BeautifulSoup(request.text, "lxml")

        if html.select_one(
            f".school_menu_info > ul:nth-child({self.number + 1}) > li:nth-child(1) > dl:nth-child(1) > dt:nth-child(1) > a:nth-child(1)"
        ).text.endswith(day_and_month):
            cafeteria = re.findall(
                "[^ \r\n\t()0-9kcal]+",
                html.select_one(
                    f".school_menu_info > ul:nth-child({self.number + 1}) > li:nth-child(1) > dl:nth-child(1) > dd:nth-child(2) > p:nth-child(2)"
                ).text,
            )

            response_head.extend(cafeteria)

            response = "\n".join(response_head)

        else:
            response = f"{self.date_}({self.day}일) 급식은 없어요."

        return _return_response(response)

    def get_timetable(self, school, grade, class_):
        weekday = (date.today() + timedelta(days=self.number)).weekday()

        try:
            week_data = school[grade][class_][weekday]

        except IndexError:
            response = f"{self.date_}({self.day}일) 시간표는 없어요."

        else:
            if week_data:
                response_head = [f"<{self.date_}({self.day}일) 시간표>"]

                for i, _ in enumerate(week_data):
                    timetable = week_data[i][0]

                    response_head.append(f"{i + 1}교시: {timetable}")

                response = "\n".join(response_head)

            else:
                response = f"{self.date_}({self.day}일) 시간표는 없어요."

        return _return_response(response)


class _Payload:
    def __init__(self, payload):
        self.payload = payload

    def get_grade_and_class(self):
        grade = re.search(
            r"\d", self.payload["action"]["detailParams"]["grade"]["origin"][0]
        ).group()
        class_ = re.search(
            r"\d", self.payload["action"]["detailParams"]["class"]["origin"][0]
        ).group()

        return (int(grade), int(class_))  # XXX: Is this the best way?

    def get_id(self):
        return self.payload["userRequest"]["user"]["id"]


class _User:
    def __init__(self, payload):
        self.payload = _Payload(payload)

    def edit_sql_data(self):
        id_ = self.payload.get_id()
        grade, class_ = self.payload.get_grade_and_class()

        try:
            _check_grade_and_class(grade, class_)

        except ValueError:
            response = "입력하신 정보는 유효하지 않은 값이예요. 다시 시도해 주세요."

        else:
            con = sqlite3.connect("db.sqlite3", isolation_level=None)
            cur = con.cursor()

            cur.execute("SELECT id FROM user WHERE id = ?", (id_,))

            is_user_info_exist = bool(cur.fetchone())

            if is_user_info_exist:
                cur.execute(
                    "UPDATE user SET grade = ?, class = ? WHERE id = ?",
                    (grade, class_, id_),
                )

            else:
                cur.execute("INSERT INTO user VALUES (?, ?, ?)", (id_, grade, class_))

            response = "입력하신 정보가 성공적으로 반영되었어요."

            con.close()  # XXX: Can we use `with` statement?

        return _return_response(response)

    def get_sql_data(self):
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()

        cur.execute(
            "SELECT grade, class FROM user WHERE id = ?", (self.payload.get_id(),)
        )

        grade_and_class = cur.fetchone()

        con.close()  # XXX: Can we use `with` statement?

        if grade_and_class is None:
            raise _NoData

        grade = grade_and_class[0]
        class_ = grade_and_class[1]

        return (grade, class_)


def _check_grade_and_class(grade, class_):
    if (
        grade == 0
        or class_ == 0
        or (grade == 1 and class_ > 8)
        or (grade == 2 and class_ > 7)
        or (grade == 3 and class_ > 3)
        or grade > 3
    ):
        raise ValueError


def _return_response(text):
    return {"version": "2.0", "template": {"outputs": [{"simpleText": {"text": text}}]}}
