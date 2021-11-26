import re

from aiohttp import ClientSession
from aiosqlite import connect

from .exception import NoData


def extract_id(payload: dict) -> str:
    return payload["userRequest"]["user"]["id"]


def extract_int(string: str):
    return int("".join([x for x in string if x.isdigit()]))


def jsonify(text: str):
    return {"version": "2.0", "template": {"outputs": [{"simpleText": {"text": text}}]}}


def search(regex: str, string: str):
    return re.search(regex, string).group()


def trim(list_: list):
    while list_ and not list_[-1]:
        del list_[-1]
    return list_


async def get(url: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def get_info(payload: dict):
    async with connect("db.sqlite3") as db:
        async with db.execute(
            "SELECT grade, class FROM user WHERE id = ?",
            (extract_id(payload),),
        ) as cursor:
            grade_and_class: tuple[int, int] = await cursor.fetchone()

    if grade_and_class is None:
        raise NoData

    grade = grade_and_class[0]
    class_ = grade_and_class[1]

    return grade, class_


async def post(url: str, data: dict):
    async with ClientSession() as session:
        async with session.post(url, data=data) as response:
            return await response.text()
