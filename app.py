import re

from flask import Flask, abort, request

from utils import edit_info, get_cafeteria, get_timetable


app = Flask("SingilE")


@app.before_request
def whitelist():
    if re.match("219[.]249[.]231[.]4[012]", request.remote_addr) is None:
        abort(404)


@app.route("/todaytimetable", methods=["POST"])
def today_timetable():
    return get_timetable(0, request.get_json())


@app.route("/nextdaytimetable", methods=["POST"])
def next_day_timetable():
    return get_timetable(1, request.get_json())


@app.route("/nextnextdaytimetable", methods=["POST"])
def next_next_day_timetable():
    return get_timetable(2, request.get_json())


@app.route("/todaycafeteria", methods=["POST"])
def today_cafeteria():
    return get_cafeteria(0)


@app.route("/nextdaycafeteria", methods=["POST"])
def next_day_cafeteria():
    return get_cafeteria(1)


@app.route("/nextnextdaycafeteria", methods=["POST"])
def next_next_day_cafeteria():
    return get_cafeteria(2)


@app.route("/infoedit", methods=["POST"])
def info_edit():
    return edit_info(request.get_json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
