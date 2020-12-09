from hyperparam import *
import pandas as pd
import numpy as np
import re
import os
import csv
import sys
from 공정위 import *
downed_all = list(map(str예외처리, os.listdir(raw_pdf_downpath)))
downed_all.sort(reverse=True)
시정_약관 = []
시정_나머지 = []
재결 = []
나머지 = []
for changed in downed_all[:10]:
    file_pdf = pdf_처리(changed,downpath=raw_pdf_downpath)
    ok,n__,dat = 문서추출(file_pdf, changed)
    if ok:
        if "시정" in n__:
            if "약관" in n__:
                시정_약관.append(dat)
            else:
                시정_나머지.append(dat)
        elif n__ == "재결":
            재결.append(dat)
        else:
            나머지.append(dat)
나머지_col = ["문서타입", "사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "주문", "심의종결일", "파일명"]
재결_col = ["문서타입", "사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "주문", "원심결", "심의종결일", "파일명"]
시정_약관_DF_col = ['문서타입', '사건번호', '시정권고', '사건명', '시정권고사항', '피심인', '적용법조', '시정권고이유']
시정_나머지_DF_col = ['문서타입', '사건번호', '시정권고', '사건명', '시정권고사항', '피심인', '적용법조', '수락거부시조치', '수락여부통지기간', '시정기한', '법위반내용']

시정_약관_DF_ = pd.DataFrame.from_dict(시정_약관).reset_index(drop=True).reindex(columns=시정_약관_DF_col)
시정_나머지_DF_ = pd.DataFrame.from_dict(시정_나머지).reset_index(drop=True).reindex(columns=시정_나머지_DF_col)
재결_DF_ = pd.DataFrame.from_dict(재결).reset_index(drop=True).reindex(columns=재결_col).rename(columns={"주문": "세부조치내역"})
나머지_DF_ = pd.DataFrame.from_dict(나머지).reset_index(drop=True).reindex(columns=나머지_col).rename(columns={"주문": "세부조치내역"})

changed = "2020-09-25@@결정2020-018@@2018내부0294고발결정서(금호)_최종.pdf"
file_pdf = pdf_처리(changed)
n__, dat = 문서추출(file_pdf)