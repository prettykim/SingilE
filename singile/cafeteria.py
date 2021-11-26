import re
from datetime import date, timedelta

from bs4 import BeautifulSoup

from .utils.functions import get


# public interface -----------------------------------------------------
async def get_cafeteria(when: int):
    day = (date.today() + timedelta(days=when)).day

    try:
        text: str = _cache[day]

    except KeyError:
        parser = _Cafeteria(when)
        text = await parser.get_cafeteria()

        _cache[day] = text

    return text


# internals ------------------------------------------------------------
_cache = {}


class _Cafeteria:
    def __init__(self, when: int):
        self.when = when

        self.day = str((date.today() + timedelta(days=when)).day)
        self.date_ = (
            "오늘"
            if when == 0
            else ("내일" if when == 1 else ("모레" if when == 2 else None))
        )

    async def get_cafeteria(self):
        josa = "는" if self.when == 2 else "은"

        if (date.today() + timedelta(days=self.when)).weekday() > 4:
            text = f"{self.date_}({self.day}일){josa} 휴일이라 급식이 없네요."

        else:
            day = "0" + self.day if len(self.day) == 1 else self.day
            month = str((date.today() + timedelta(days=self.when)).month)
            day_and_month = ("0" + month if len(month) == 1 else month) + "." + day

            response = await get("https://singil.sen.ms.kr/index.do")
            soup = BeautifulSoup(response, "lxml")

            text = f"{self.date_}({self.day}일){josa} 휴일이라 급식이 없네요."

            for i in range(1, 4):
                base_selector = f".school_menu_info > ul:nth-child({i}) > li:nth-child(1) > dl:nth-child(1) > "

                try:
                    is_today_caferia = soup.select_one(
                        base_selector + "dt:nth-child(1) > a:nth-child(1)"
                    ).text.endswith(day_and_month)

                except AttributeError:
                    text = "제가 찾아보니 아직 학교 급식 메뉴가 업데이트 되지 않았네요. 잠시 후 다시 물어봐 주세요."

                else:
                    if is_today_caferia:
                        header = [f"<{self.date_}({self.day}일) 급식>"]

                        cafeteria: list[str] = re.findall(
                            "[가-힣]+[(]?[ &,가-힣]+[)]?",
                            soup.select_one(
                                base_selector + "dd:nth-child(2) > p:nth-child(2)"
                            ).text,
                        )

                        for j in cafeteria:
                            menu = j.replace("(", "\n(").replace("&", "\n")

                            header.append(menu)

                        text = "\n".join(header)

                    else:
                        continue

                break

        return text
