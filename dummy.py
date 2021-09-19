import logging
from datetime import datetime


def leave_log(payload: dict):
    logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s[%(levelname)s]: %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(
        f"{datetime.now().strftime('%Y%m%d%H%M%S')}.log", encoding="UTF-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(payload["userRequest"]["utterance"])
