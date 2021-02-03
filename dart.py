import OpenDartReader
import pandas as pd
api_key = '52b29a8be37caf5452089a036128f5bc0b8f2e78'

dart = OpenDartReader(api_key)

def 배당_최대주주_data(회사명,년도 = None):
    import datetime
    if 년도 is None:
        년도 = range(2010,datetime.date.today().year+1)
    try:
        float(회사명)
        code = 회사명
    except:
        code = dart.find_corp_code(회사명)
    if code is None:
        return None, None
    try:
        배당 = pd.concat([dart.report(code, '배당', y) for y in 년도])
    except:
        배당 =None
    try:
        최대주주 = pd.concat([dart.report(회사명, '최대주주', y) for y in 년도])
    except:
        최대주주 = None
    #최대주주변동 = pd.concat([dart.report(회사명, '최대주주변동', y) for y in 년도])
    return 배당,최대주주#최대주주변동
def 기업집단_data(저장이름,회사들,년도 = None,save=False):
    배당 = []
    최대주주 = []
    for 회사명 in 회사들:
        a,b = 배당_최대주주_data(회사명, 년도=년도)
        if a is not None:
          배당.append(a)
        if b is not None:
          최대주주.append(b)
    배당 = pd.concat(배당)
    최대주주 = pd.concat(최대주주)
    if save:
        배당.to_excel(f"{저장이름}_배당.xlsx")
        최대주주.to_excel(f"{저장이름}_최대주주.xlsx")
    return 배당,최대주주

#집단 지배구조
삼성 = ["삼성물산","삼성에스디에스","삼성엔지니어링","삼성전자","삼성화재해상보험"]
#현대 =  ["현대글로비스","현대엔지니어링","해비치호텔앤드리조트","현대자동차","현대모비스","이노션","현대위아","현대오토에버","기아자동차","현대엔지니어링","서림개발"]
#SK = ["034730","017670","006120","285130","096770","216050","036490"]
#LG = ["003550","066570","051900","051910","001120"]
#롯데 = ["롯데지주","롯데케미칼","롯데푸드","롯데쇼핑","롯데정보통신","롯데제과"]
#한화 = ["한화","한화에어로스페이스","한화솔루션","한화시스템",]
#기업집단 = pd.concat(list(map(pd.Series,[삼성,현대,SK,LG,롯데,한화])),axis=1)
#기업집단.columns = ["삼성","현대","SK","LG","롯데","한화"]
#기업집단.to_excel("기업집단지배구조.xlsx")
기업집단 = pd.read_excel("기업집단지배구조.xlsx")
for n,dat in 기업집단.iteritems():
    try:
        기업 = dat.dropna().astype("int").astype("str").tolist()
    except:
        기업 = dat.dropna().astype("str").tolist()
    기업집단_data(n,기업,년도 = None,save=False)

