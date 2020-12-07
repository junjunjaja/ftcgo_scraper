import pandas as pd
import numpy as np
import re
import pdftotext
import os
import webbrowser
import csv
import sys
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/100)


#downpath =r"C:\Users\junlee\Desktop\CODE\Python\corona\ftc_go_file"
downpath = r"C:\Users\junlee\Desktop\CODE\Python\corona\scrapdart"
파일select = re.compile("\w+_to[0-9]{3,}\.csv")
파일select = [파일select.search(i).group() for i in os.listdir(downpath) if 파일select.search(i) is not None]
#,usecols = list(range(0,14))
나머지_col = ["사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "세부조치내역"]
재결_col = ["사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "세부조치내역"]
시정_약관_DF_col = ['문서타입', '사건번호',"의결번호",'사건명', '시정권고',"의결일", '피심인','시정권고사항', '적용법조']
시정_나머지_DF_col = ['문서타입', '사건번호', "의결번호" ,'사건명',"대표조치유형",'의결일','시정권고','시정권고사항', '피심인','법위반내용','수락거부시조치', '수락여부통지기간', '시정기한']
시정나머지 =[]
시정약관 = []
의결서 = []
재결 = []
for i in 파일select:
    if "나머지" in i:
        시정나머지.append(i)
    elif "의결서" in i:
        의결서.append(i)
    elif "재결" in i:
        재결.append(i)
    elif "약관" in i:
        시정약관.append(i)
for n,k,l in zip([나머지_col,재결_col,시정_약관_DF_col,시정_나머지_DF_col],[의결서,재결,시정약관,시정나머지],["의결서","재결","시정약관","시정나머지"]):
    if l == "의결서":
        a = pd.concat([pd.read_csv(f"{downpath}\{i}",engine='python',encoding= "UTF-8",index_col=0,verbose= True) for i in k],axis=0).reset_index().reindex(columns=n)
        a.to_excel(f"{l}.xlsx")
a["문서타입"].drop_duplicates()
a[a["사건번호"].isna()]["파일명"]



def pdf_처리(pdf_name,downpath = downpath,n = None):
    file = open(downpath+"\\"+pdf_name, 'rb')
    fileReader = pdftotext.PDF(file)
    file = ""
    if n is None:
        n = len(fileReader)
    for i in range(n):
        file += re.compile("- {0,}[0-9] {0,}- {0,}").sub("",fileReader[i]) + f" - {i} - "
    file = cleansing(file)
    return file
def cleansing(file):
    #c = re.compile(r"(\w)( {2,})(\w)")
    #for _ in range(1):
    #    file = c.sub(r"\1\3", file)
    white = re.compile("[' ','\t','\n','\r','\x0b','\x0c']")
    file = white.sub(" ", file)
    #file = " ".join(re.split(" {2,}", file))
    return file

def 찾기(recomp,x):
    if recomp.search(x) is not None:
        return [i for i in recomp.search(x).groups() if i is not None]
    else:
        return pd.NaT

특문 = "「」".replace("","|")[1:-1]
df = pd.read_pickle(r"C:\Users\junlee\Desktop\CODE\Python\corona\scrapdart\임시.p")
개별번호 = re.compile("([0-9]{1,}\. {1,})(\w+\W+){1,3}")
당사자 = re.compile("(\w+(?:\. )?\w+)(?:\([주유]\))?의?[\b\W]")

re.search("\w+의[\b\W]","DONGJUND. home의 가맹사업법")
for i in re.finditer("(\w)+(\([주유]\))?의[\b\W]","세종라이프(주)의 경고심의요청"):
    print(i.group())
df["사건명"].iloc[59]
주식회사 = re.compile("(?:\(주\)(\w+))|(?:(\w+)\(주\))")
유한 = re.compile("\(유\)\w+|\w+\(유\)")
기업집단 = re.compile(r"(기업집단) {0,}[「」]? {0,}(\w+) {0,}[「」]?")
v = df.iloc[2,:].values
개별번호.findall(v[6])
df["사건명"].apply(lambda x: 찾기(당사자,x))[50:60]
df["사건명"].apply(lambda x: 당사자.findall(x))[50:60]
df["사건명"].apply(lambda x: 찾기(주식회사,x))
df["사건명"].apply(lambda x: 주식회사.findall(x))
df["사건명"].apply(lambda x: 찾기(기업집단,x)).dropna()
df["사건명"][df["사건명"].apply(lambda x: "기업집단" in x)]
df["피심인"].apply(lambda x: 개별번호.findall(x))
