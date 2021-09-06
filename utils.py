import sqlite3
from datetime import date, timedelta


class NoDataError(Exception):
    pass


class UtteranceError(Exception):
    pass


class User:
    def __init__(self, payload):
        self.payload = _Payload(payload)

    def edit_sql_data(self):
        id_ = self.payload.get_id()
        grade, class_ = self.payload.get_grade_and_class_()

        check_grade_and_class_(grade, class_)

        con = sqlite3.connect("database.db", isolation_level=None)
        cur = con.cursor()

        cur.execute("SELECT id FROM user WHERE id = ?", (id_,))
        is_user_info_exist = cur.fetchone()

        if is_user_info_exist is None:
            cur.execute("INSERT INTO user VALUES (?, ?, ?)", (id_, grade, class_))

        else:
            cur.execute(
                "UPDATE user SET grade = ?, class_ = ? WHERE id = ?",
                (grade, class_, id_),
            )

        con.close()

    def get_sql_data(self):
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        cur.execute(
            "SELECT grade, class_ FROM user WHERE id = ?", (self.payload.get_id(),)
        )
        info = cur.fetchone()

        if info is None:
            con.close()

            raise NoDataError

        con.close()

        return info[0], info[1]


def check_grade_and_class_(grade, class_):
    if (
        grade == 0
        or class_ == 0
        or (grade == 1 and class_ > 8)
        or (grade == 2 and class_ > 7)
        or (grade == 3 and class_ > 3)
        or grade > 3
    ):
        raise ValueError


def get_time(number):
    return (
        (date.today() + timedelta(days=number)).day,
        (date.today() + timedelta(days=number)).weekday(),
        "오늘"
        if number == 0
        else ("내일" if number == 1 else ("모레" if number == 2 else None)),
    )


def get_timetable(school, grade, class_, day, weekday, date_):
    try:
        timetable = f"<{date_}({day}일) 시간표>"

        for i in range(len(school[grade][class_][weekday])):
            timetable_class = school[grade][class_][weekday][i][0]

            timetable += f"\n{i + 1}교시: {timetable_class}"

    except IndexError:
        timetable = f"{date_}({day}일) 시간표는 없어요."

    finally:
        return timetable


def return_response(text):
    return {"version": "2.0", "template": {"outputs": [{"simpleText": {"text": text}}]}}


class _Payload:
    def __init__(self, payload):
        self.payload = payload

    def get_grade_and_class_(self):
        return (
            int(self.payload["action"]["detailParams"]["grade"]["origin"][0]),
            int(self.payload["action"]["detailParams"]["class_"]["origin"][0]),
        )

    def get_id(self):
        return self.payload["userRequest"]["user"]["id"]

    def get_utterance(self):
        return self.payload["userRequest"]["utterance"]
