class NoData(Exception):
    def __str__(self):
        return """누락된 설정이 있어요.
신길이 이용을 위해서
학년과 반 정보를 설정해 주세요.

<명령어>
오늘 시간표, 내일 시간표,
모레 시간표, 오늘 급식, 내일 급식,
모레 급식, 정보 수정, 도움말"""
