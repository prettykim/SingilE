from fastapi import FastAPI, Request

from utils import edit_info, get_cafeteria, get_timetable


app = FastAPI()


@app.post("/todaytimetable")
async def today_timetable(payload: Request):
    return await get_timetable(0, await payload.json())


@app.post("/nextdaytimetable")
async def next_day_timetable(payload: Request):
    return await get_timetable(1, await payload.json())


@app.post("/nextnextdaytimetable")
async def next_next_day_timetable(payload: Request):
    return await get_timetable(2, await payload.json())


@app.post("/todaycafeteria")
async def today_cafeteria():
    return await get_cafeteria(0)


@app.post("/nextdaycafeteria")
async def next_day_cafeteria():
    return await get_cafeteria(1)


@app.post("/nextnextdaycafeteria")
async def next_next_day_cafeteria():
    return await get_cafeteria(2)


@app.post("/infoedit")
async def info_edit(payload: Request):
    return await edit_info(await payload.json())
