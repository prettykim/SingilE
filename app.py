from flask import Flask, request

from school_edited import SchoolEdited
from utils import NoDataError, User, get_time, get_timetable, return_response


app = Flask("SingilE")

school = SchoolEdited("신길중학교")


@app.route("/timetabletoday", methods=["POST"])
def timetable_today():
    day, weekday, date_ = get_time(0)

    payload = request.get_json()

    user_info = User(payload)

    try:
        grade, class_ = user_info.get_sql_data()

    except NoDataError:
        text = """누락된 설정이 있어요.
신길이 이용을 위해서 학년과 반 정보를 설정해 주세요.

<명령어>
오늘시간표, 내일시간표, 모레시간표, 정보설정, 도움말"""

    else:
        text = get_timetable(school, grade, class_, day, weekday, date_)

    finally:
        return return_response(text)


@app.route("/timetablenextday", methods=["POST"])
def timetable_next_day():
    day, weekday, date_ = get_time(1)

    payload = request.get_json()

    user_info = User(payload)

    try:
        grade, class_ = user_info.get_sql_data()

    except NoDataError:
        text = """누락된 설정이 있어요.
신길이 이용을 위해서 학년과 반 정보를 설정해 주세요.

<명령어>
오늘시간표, 내일시간표, 모레시간표, 정보설정, 도움말"""

    else:
        text = get_timetable(school, grade, class_, day, weekday, date_)

    finally:
        return return_response(text)


@app.route("/timetablenextnextday", methods=["POST"])
def timetable_next_next_day():
    day, weekday, date_ = get_time(2)

    payload = request.get_json()

    user_info = User(payload)

    try:
        grade, class_ = user_info.get_sql_data()

    except NoDataError:
        text = """누락된 설정이 있어요.
신길이 이용을 위해서 학년과 반 정보를 설정해 주세요.

<명령어>
오늘시간표, 내일시간표, 모레시간표, 정보설정, 도움말"""

    else:
        text = get_timetable(school, grade, class_, day, weekday, date_)

    finally:
        return return_response(text)


@app.route("/editinfo", methods=["POST"])
def edit_info():
    payload = request.get_json()

    user_info = User(payload)

    try:
        user_info.edit_sql_data()

    except ValueError:
        text = "입력하신 정보는 유효하지 않은 값이예요. 다시 시도해 주세요."

    else:
        text = "입력하신 정보가 성공적으로 반영되었어요."

    finally:
        return return_response(text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
