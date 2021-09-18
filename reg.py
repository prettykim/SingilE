import re


reg_daydata = re.compile(r"일일자료=자료\.자료\d+")
reg_prefix = re.compile(r"'\d+_'")
reg_route = re.compile(r"\./\d+\?\d+l")
reg_sbname = re.compile(r"자료.자료\d+\[sb\]")
reg_thname = re.compile(r"성명=자료\.자료\d+")


def extract_int(org):
    return int("".join([x for x in org if x.isdigit()]))


def search_reg(reg, org):
    return reg.search(org).group(0)
