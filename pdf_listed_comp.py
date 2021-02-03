from hyperparam import *
import pandas as pd
import numpy as np
import re
import os
import csv
import sys
#from pykrx import stock
def voca_re_make(string):
    voca = r"(?:(?:\(주\))|(?: *))"+string+r"(?:(?:\(주\))|(?: *))"
    return voca
def find_voca(string,target):
    return re.compile(string).search(target)

def load_complete_ftc_file(save=False,제출용=True):
    파일select = re.compile("\w+_to[0-9]{3,}\.xlsx")
    파일select = [파일select.search(i).group() for i in os.listdir(pre_clean_path) if 파일select.search(i) is not None]
    # ,usecols = list(range(0,14))
    나머지_col = ["사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "세부조치내역"]
    재결_col = ["사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "세부조치내역"]
    시정_약관_DF_col = ['문서타입', '사건번호', "의결번호", '사건명', '시정권고', "의결일", '피심인', '시정권고사항', '적용법조']
    시정_나머지_DF_col = ['문서타입', '사건번호', "의결번호", '사건명', "대표조치유형", '의결일', '시정권고', '시정권고사항', '피심인', '법위반내용', '수락거부시조치',
                     '수락여부통지기간', '시정기한']
    에러_col = ["다운오류","파일명변경오류","파일오류","추출오류"]
    시정나머지 = []
    시정약관 = []
    의결서 = []
    재결 = []
    에러 = []
    for i in 파일select:
        if "나머지" in i:
            시정나머지.append(i)
        elif "의결서" in i:
            의결서.append(i)
        elif "재결" in i:
            재결.append(i)
        elif "약관" in i:
            시정약관.append(i)
        elif "err" in i:
            에러.append(i)
    all_df = []
    for n, k, l in zip([나머지_col, 재결_col, 시정_약관_DF_col, 시정_나머지_DF_col,에러_col], [의결서, 재결, 시정약관, 시정나머지,에러],
                       ["의결서", "재결", "시정약관", "시정나머지","err"]):
        if 제출용:
            a = pd.concat(
                [pd.read_excel(f"{pre_clean_path}\{i}",encoding="UTF-8", index_col=0, verbose=True) for i in
                 k], axis=0).reset_index().reindex(columns=n)
        else:
            a = pd.concat(
                [pd.read_excel(f"{pre_clean_path}\{i}", encoding="UTF-8", index_col=0, verbose=True) for i in
                 k], axis=0).reset_index()
        if save:
            a.to_excel(f"{clean_df}{l}.xlsx")
        all_df.append(a)
    return all_df

def get_tickers(save=False):
    tickers = [stock.get_market_ticker_list(f"{y}0225") for y in range(1985,2021)]
    tickers = pd.concat(tickers)
    tickers = tickers.drop_duplicates()
    name = tickers.apply(lambda x: stock.get_market_ticker_name(x))
    tickers = pd.concat([tickers,name],axis=1)
    tickers.columns = ["ticker","name"]
    tickers["name"] = tickers["name"].apply(strip)
    if save:
        tickers.to_pickle(피클경로+"tickers.pickle")
    return tickers

def strip(string):
    return string.replace(" ","")
def firm_exist_1(string,tickers,strip_=True):
    if strip_:
        a = [name for name in tickers["name"].tolist() if name in strip(string)]
    else:
        a = [name for name in tickers["name"].tolist() if name in string]
    if len(a) >=1:
        return a
    else:
        return pd.NaT
def firm_exist_2(string,tickers,strip_=False):
    if strip_:
        a = [name for name in tickers["name"].tolist() if find_voca(voca_re_make(name),strip(string)) is not None]
    else:
        a = [name for name in tickers["name"].tolist() if find_voca(voca_re_make(name),string) is not None ]
    if len(a) >=1:
        return a
    else:
        return pd.NaT
if __name__ == "__main__":
    pre_clean_path += "/ver_1"
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt / 100)
    #tickers = get_tickers()
    load_complete_ftc_file(save=True,제출용=False)

    tickers = pd.read_pickle(피클경로+"tickers.pickle")
    a = pd.read_excel(clean_df+"의결서.xlsx")
    a_ = pd.read_excel(clean_df+"재결.xlsx")
    a = pd.concat([a,a_],axis=0)
    del a_
    a["피심인_기업"] = a["피심인"].astype(str).apply(lambda x: firm_exist_1(x,tickers))
    a["사건명_기업"] = a["사건명"].astype(str).apply(lambda x: firm_exist_1(x, tickers))
    a["세부조치_기업"] = a["세부조치내역"].astype(str).apply(lambda x: firm_exist_1(x, tickers))
    b = a.dropna(subset=["피심인_기업","사건명_기업"],how="all")
    c = pd.DataFrame()
    b.to_pickle(피클경로+"b.pickle")
    c["피심인_기업"] = b["피심인"].astype(str).apply(lambda x: firm_exist_2(x, tickers))
    c["사건명_기업"] = b["사건명"].astype(str).apply(lambda x: firm_exist_2(x, tickers))
    c["세부조치_기업"] = b["세부조치내역"].astype(str).apply(lambda x: firm_exist_2(x, tickers))
    c.to_pickle(피클경로 + "c.pickle")
    b = pd.read_pickle(피클경로 + "b.pickle")
    c = pd.read_pickle(피클경로 + "c.pickle")

    b = pd.read_pickle(피클경로 + "b.pickle")
    c = pd.read_pickle(피클경로 + "c.pickle")
    b_ = b[["피심인_기업", "사건명_기업", "세부조치_기업"]]
    c = c.fillna("").apply(lambda x: x.apply(lambda x: ",".join(x)))
    b_ = b_.fillna("").apply(lambda x: x.apply(lambda x: ",".join(x)))
    c = c["피심인_기업"] + "," + c["사건명_기업"]
    c = c.apply(lambda x: list(set(x.split(",")) - set([""])))
    b["해당기업"] = c
    b = b.drop(["피심인_기업", "사건명_기업", "세부조치_기업"], axis=1)
    b = b.dropna(subset=["해당기업"])
    tickers = tickers.set_index("name")
    a = []
    for n, i in b.iterrows():
        기업 = i["해당기업"]
        for j in 기업:
            k = i.to_dict()
            k["해당기업"] = j
            try:
                k["기업ticker"] = tickers.loc[j][0]
            except:
                k["기업ticker"] = ""
            a.append(k)
    a = pd.DataFrame.from_dict(a)
    a = pd.DataFrame.from_dict(a)
    a = a.rename(columns={"Unnamed: 0": "origin_index"})
    a.to_excel("상장기업정리.xlsx")


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
