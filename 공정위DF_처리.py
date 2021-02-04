import pandas as pd
import re
def 문자열사이공백(string,n=0,m=None):
    strings = [i for i in string]
    if n is None:
        a = f",{m}"
    elif m is None:
        a = f"{n},"
    else:
        a = f"{n},{m}"
    n,m= 1,3
    a = r"\s{" + a +"}"
    return a.join(strings)
def 단어찾기(df,string,col="사건명",포함=True):
    a = re.compile(문자열사이공백(string))
    if 포함:
        b = df.loc[df[col].apply(lambda x: True if a.search(x) is not None else False)]
    else:
        b = df.loc[df[col].apply(lambda x: False if a.search(x) is not None else True)]
    return b
def 단어포함제외(df,string,col="사건명",포함=True):
    d = 단어찾기(df,string,col,포함).copy()
    not_cate = df[~df.index.isin(d.index)]
    return not_cate,d

DF = pd.read_excel("상장기업정리.xlsx",engine='openpyxl',index_col=0)
s = ["부당한공동행위","불공정하도급거래","계열회사의부당지원행위","허위자료제출"]
searc = ["공동행위","불공정","계열","자료"]
dat = []
for i,j in zip(s,searc):
    d = 단어찾기(DF,j).copy()
    if j == "불공정":
        d2 = 단어찾기(d,"하도급",포함=False)
        d3 = 단어찾기(단어찾기(d2,"거래"),"조항",포함=False)
        d3["사건유형대분류"] = "불공정거래"
        dat.append(d3)
        d4 = pd.concat([단어찾기(d2, "조항"),단어찾기(d2, "약관")])
        d4 = d4[~d4.duplicated()]
        d4["사건유형대분류"] = "불공정조항약관"
        dat.append(d4)
        dd = d2[~d2.index.isin(pd.concat([d3,d4]).index)]
        dd["사건유형대분류"] = "개별기업불공정행위"
        dat.append(dd)
        d = 단어찾기(d, "하도급")
        d["사건유형대분류"] = i
        dat.append(d)
    elif j =="계열":
        d["사건유형대분류"] = i
        d2 = 단어찾기(d, "부당", 포함=False)
        d2["사건유형대분류"] = "계열사관련부당지원외"
        dat.append(d)
        dat.append(d2)
    else:
        d["사건유형대분류"] = i
        dat.append(d)
def 사건유형대분류추가(df,string):
    global new_dat
    df["사건유형대분류"] = string
    new_dat.append(df)

dat = pd.concat(dat)

dat["사건유형대분류"].drop_duplicates()
#dup = dat[dat.index.duplicated(keep=False)]
not_cate = DF[~DF.index.isin(dat.index)]
s = ["부당한공동행위","불공정하도급거래","계열회사의부당지원행위","허위자료제출"]
searc = ["공동행위","불공정","계열","자료"]
new_dat = []
not_cate,d5 = 단어포함제외(not_cate,"사업자단체") #부당한공동행위
사건유형대분류추가(d5,"부당한공동행위")
not_cate,d5 = 단어포함제외(not_cate,"그룹") #부당한공동행위
사건유형대분류추가(d5,"부당한공동행위")
not_cate,d5 = 단어포함제외(not_cate,"지위") #불공정하도급거래
사건유형대분류추가(d5,"불공정하도급거래")
not_cate,d5 = 단어포함제외(not_cate,"가맹사업") #개별기업불공정행위
사건유형대분류추가(d5,"개별기업불공정행위")
not_cate,d5 = 단어포함제외(not_cate,"광고") #개별기업불공정행위 #광고
사건유형대분류추가(d5,"개별기업불공정행위")
not_cate,d5 = 단어포함제외(not_cate,"불이행") #시정조치 불이행
사건유형대분류추가(d5,"시정조치불이행")
not_cate,d5 = 단어포함제외(not_cate,"내부거래") #내부거래
사건유형대분류추가(d5,"내부거래")
not_cate,d5 = 단어포함제외(not_cate,"자회사") #자회사행위규정위반
사건유형대분류추가(d5,"자회사행위규정위반")
not_cate,d5 = 단어포함제외(not_cate,"상호출자") #계열회사 관련 부당지원 외
d5,d6 = 단어포함제외(d5,"부당지원") #계열회사의부당지원행위
사건유형대분류추가(d5,"계열사관련부당지원외")
사건유형대분류추가(d6,"계열회사의부당지원행위")

not_cate,d5 = 단어포함제외(not_cate,"상호출자") #계열회사 관련 부당지원 외
사건유형대분류추가(d5,"계열회사의부당지원행위")

not_cate,d5 = 단어포함제외(not_cate,"지주") #지주회사행위제한
사건유형대분류추가(d5,"지주회사행위제한")

not_cate,d5 = 단어포함제외(not_cate,"직원") #조사방해 행위
사건유형대분류추가(d5,"조사방해행위")

not_cate,d5 = 단어포함제외(not_cate,"부당지원") #부당지원
사건유형대분류추가(d5,"계열회사의부당지원행위")
not_cate,d5 = 단어포함제외(not_cate,"과징금") #과징금 납부 연장
사건유형대분류추가(d5,"과징금납부연장")
not_cate,d5 = 단어포함제외(not_cate,"이의신청") #이의신청
사건유형대분류추가(d5,"이의신청")
not_cate,d5 = 단어포함제외(not_cate,"공동") #부당한공동행위
사건유형대분류추가(d5,"부당한공동행위")

#not_cate,d5 = 단어포함제외(not_cate,"소비자") #소비자보호법 위반
#not_cate,d5 = 단어포함제외(not_cate,"유통업") #유통업법 위반
#not_cate,d5 = 단어포함제외(not_cate,"판매") #판매관련

not_cate,d5 = 단어포함제외(not_cate,"부당한지원")  #부당한공동행위
사건유형대분류추가(d5,"부당한공동행위")

not_cate,d5 = 단어포함제외(not_cate,"불동정")  #불공정조항약관
사건유형대분류추가(d5,"불공정조항약관")

not_cate,d5 = 단어포함제외(not_cate,"집단")  #불공정조항약관
사건유형대분류추가(d5,"불공정조항약관")

사건유형대분류추가(not_cate,"개별기업불공정행위")

new_dat = pd.concat(new_dat)

data_all = pd.concat([dat,new_dat])
data_all = data_all[~data_all.index.duplicated(keep='last')]

data_all = data_all[['origin_index','사건번호', '의결번호', '사건명','사건유형대분류', '대표조치유형', '의결일', '피심인', '세부조치내역','해당기업', '기업ticker']]
data_all.to_excel("사건유형대분류.xlsx")

data_all.groupby("사건유형대분류").count().loc[:,"사건명"].to_excel("대분류유형별개수.xlsx")

print(data_all["사건유형대분류"].drop_duplicates().to_list())

a = not_cate.loc[not_cate["사건명"].apply(lambda x: True if re.compile("부당지원").search(x) is not None else False)]
"부당한 공동행위"
r"\d개 부당한 공동행위"
"사업자단체"

"계열회사들의 부당지원 행위"
"부당이익제공행위 부당지원행위"
"상호출자제한 기업집단"

"불공정하도급 거래"
"거래강제행위"

"부당 광고행위"

"사업활동방해"

"허위자료 제출"
"허위제출행위"


pd.read_excel()
