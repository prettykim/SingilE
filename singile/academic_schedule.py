import re
from datetime import date

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from .utils.functions import post


# public interface -----------------------------------------------------
async def get_academic_schedule(when: int):
    month = (date.today() + relativedelta(months=when)).month

    try:
        text: str = _cache[month]

    except KeyError:
        text = await _get_academic_schedule(when)

        _cache[month] = text

    return text


# internals ------------------------------------------------------------
_cache = {}


async def _get_academic_schedule(when: int):
    month = (date.today() + relativedelta(months=when)).month
    year = (date.today() + relativedelta(months=when)).year

    html = await post(
        "https://singil.sen.ms.kr/177194/subMenu.do",
        {
            "siteId": "SEI_00002286",
            "viewType": "list",
            "arrSchdulId": 0,
            "srhSchdulYear": year,
            "srhSchdulMonth": month,
        },
    )

    soup = BeautifulSoup(html, "lxml")

    header = [f"<이번 달({month}월) 학사일정>"] if when == 0 else [f"<다음 달({month}월) 학사일정>"]

    for i in range(1, 32):
        base_selector = (
            f".board_type01_tb_list > tbody:nth-child(4) > tr:nth-child({i})"
        )

        try:
            start = soup.select_one(base_selector + " > td:nth-child(1)").text
            end = soup.select_one(base_selector + " > td:nth-child(2)").text
            schedule = re.search(
                r"[^()]+",
                soup.select_one(
                    base_selector + " > td:nth-child(3) > a:nth-child(1)"
                ).text,
            ).group()

            header.append(schedule)

            day_start = re.search(r"[1-9][\d]?", start[8:10]).group()

            if start[8:10] == end[8:10]:
                header.append(f"({day_start}일({start[11]}))")

            else:
                day_end = re.search(r"[1-9][\d]?", end[8:10]).group()

                header.append(f"({day_start}일({start[11]})~{day_end}일({end[11]}))")

        except AttributeError:
            break

    text = "\n".join(header)

    return text
