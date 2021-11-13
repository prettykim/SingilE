import re

import aiosqlite

from .utils.functions import extract_id


async def edit_info(payload: dict):
    id_ = extract_id(payload)
    grade = int(
        re.search(
            r"\d", payload["action"]["detailParams"]["grade"]["origin"][0]
        ).group()
    )
    class_ = int(
        re.search(
            r"\d", payload["action"]["detailParams"]["class"]["origin"][0]
        ).group()
    )

    if (
        grade == 0
        or class_ == 0
        or (grade == 1 and class_ > 8)
        or (grade == 2 and class_ > 7)
        or (grade == 3 and class_ > 3)
        or grade > 3
    ):
        text = "잘못 입력하신 것 같아요. 다시 시도해 주세요."

    else:
        async with aiosqlite.connect("db.sqlite3") as db:
            async with db.execute("SELECT id FROM user WHERE id = ?", (id_,)) as cursor:
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

        text = "입력하신 정보가 성공적으로 반영되었어요."

    return text
