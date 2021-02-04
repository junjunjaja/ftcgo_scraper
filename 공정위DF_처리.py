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


DF = pd.read_excel("상장기업정리.xlsx",engine='openpyxl',index_col=0)
s = ["부당한공동행위","불공정하도급거래","계열회사의부당지원행위","허위자료제출"]
dat = []
for i in s:
    a = re.compile(문자열사이공백(i))
    d = DF.loc[DF["사건명"].apply(lambda x: True if a.search(x) is not None else False)]
    d["사건유형대분류"] = i
    dat.append(d)
dat = pd.concat(dat)
#dup = dat[dat.index.duplicated(keep=False)]
bad_df = DF.index.isin(dat.index)
not_cate = DF[~bad_df]
re.compile("([계열회사].*|[부당한?\s?이익제공])")
dat.index.has_duplicates

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
