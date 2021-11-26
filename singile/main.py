from fastapi import FastAPI, Request

from .academic_schedule import get_academic_schedule
from .cafeteria import get_cafeteria
from .info import edit_info
from .timetable import get_timetable
from .utils.constants import COMMANDS, ERROR_MESSAGE
from .utils.functions import jsonify

app = FastAPI()


# basic scenario -------------------------------------------------------
@app.post("/fallback")
async def fallback(payload: Request):
    json: dict = await payload.json()
    utterance = json["userRequest"]["utterance"]

    if utterance == "ㅎㅇ":
        text = "ㅎㅇ"

    elif utterance == "민주공주":
        text = "✨👸✨"

    else:
        text = f"""죄송해요. 잘 이해하지 못했어요.
입력 가능한 명령어는
다음과 같아요.

{COMMANDS}"""

    return jsonify(text)


# custom scenario ------------------------------------------------------
@app.post("/timetable/{when}")
async def timetable(when: int, payload: Request):
    try:
        return jsonify(await get_timetable(when, await payload.json()))

    except Exception as e:
        print(e)

        return jsonify(ERROR_MESSAGE)


@app.post("/cafeteria/{when}")
async def cafeteria(when: int):
    try:
        return jsonify(await get_cafeteria(when))

    except Exception as e:
        print(e)

        return jsonify(ERROR_MESSAGE)


@app.post("/info")
async def info(payload: Request):
    try:
        return jsonify(await edit_info(await payload.json()))

    except Exception as e:
        print(e)

        return jsonify(ERROR_MESSAGE)


@app.post("/academic-schedule/{when}")
async def academic_schedule(when: int):
    try:
        return jsonify(await get_academic_schedule(when))

    except Exception as e:
        print(e)

        return jsonify(ERROR_MESSAGE)


@app.post("/help")
async def help_():
    return jsonify(
        f"""안녕하세요!
자세한 정보는
아래에서 보실 수 있어요.
좋은 하루 되세요!

{COMMANDS}

<문의하기>
mg7441081@gmail.com

<기여하기>
https://github.com/HolyDiamonds7/SingilE"""
    )
