import os
import sys
from datetime import datetime
from shutil import copyfile

from uvicorn import run

from singile.main import app


def main():
    cls()

    print("---------------------------------------------")
    print(" 1. 서버 실행")
    print(" 2. DB 백업")
    print(" 3. 스크립트 종료")
    print("---------------------------------------------")

    command1 = input("원하는 항목의 번호를 입력하고 엔터(Enter): ")

    if command1 == "1":
        cls()

        run(app, host="0.0.0.0", port=50114)

    elif command1 == "2":
        try:
            os.mkdir("backup")

        except FileExistsError:
            pass

        os.chdir("backup")

        copyfile(r"..\db.sqlite3", f"{datetime.now().strftime('%Y%m%d%H%M%S')}.sqlite3")

    elif command1 == "3":
        sys.exit()

    else:
        main()

    sub()


def sub():
    cls()

    print("---------------------------------------------")
    print(" 1. 메인 화면으로 복귀")
    print(" 2. 스크립트 종료")
    print("---------------------------------------------")

    command2 = input("원하는 항목의 번호를 입력하고 엔터(Enter): ")

    if command2 == "1":
        main()

    elif command2 == "2":
        sys.exit()

    else:
        sub()


def cls():
    os.system("cls")


if __name__ == "__main__":
    main()
