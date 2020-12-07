from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException as ENIE
from selenium.common.exceptions import UnexpectedAlertPresentException as UAP
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import lxml.html
import re
from pathlib import Path
import os
import re
import pdftotext
import string
from contextlib import suppress
#downpath =r"C:\Users\junlee\Downloads"
downpath =r"C:\Users\junlee\Desktop\CODE\Python\corona\ftc_go_file"
def chromeoptionset():
    #option 추가 할거 있으면 여기 하기
    options = webdriver.ChromeOptions()
    #options.add_argument('headless')
    options.add_argument("disable-gpu")
    options.add_argument("lang=ko_KR")  # 한국어!
    #options.add_argument("proxy-server=localhost:8080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    options.add_experimental_option("prefs", {
        "download.default_directory": downpath,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        'profile.default_content_setting_values.automatic_downloads': 1
    })
    return options

def str예외처리(name):
    name = name.replace("］", "]").replace("?","_")
    return name
def is_download_finished(temp_folder,files = None):
    #file이 없을때는 모두 download가 완료되었는지 check
    #file이 있을 경우 file이 download 시도가 되어 존재하는지 check --> 있으면 down안할거임
    firefox_temp_file = sorted(Path(temp_folder).glob('*.part'))
    chrome_temp_file = sorted(Path(temp_folder).glob('*.crdownload'))
    downloaded_files = sorted(Path(temp_folder).glob('*.*'))
    if files is None:
        pass
    else:
        chrome_temp_file = [i for i in chrome_temp_file for j in files if j.split(".")[0] in str예외처리(i.stem)]
        downloaded_files = [i for i in downloaded_files for j in files if j in str예외처리(i.name)]

        if (len(downloaded_files) >=1) or (len(chrome_temp_file) >=1) :
            return True
    if (len(firefox_temp_file) == 0) and \
       (len(chrome_temp_file) == 0) and \
       (len(downloaded_files) >= 1):
        return True
    else:
        return False
def 의결서_click(driver,의결서,n):
    try:
        with suppress(ENIE) : driver.find_element_by_xpath(f"//*[@id='ltfrList']/tbody/tr[{n}]/td[6]/a").click()
        #의결서.find_element_by_class_name("down_files.pdf").click()
        element = WebDriverWait(driver, 10).until(EC.alert_is_present()).accept()
        #alert = driver.switch_to.alert
        #alert.accept()
        print("alert accepted")
        #driver.implicitly_wait(imp_time2)
        return True
    except TimeoutException:
        무의미한클릭(action, driver)
        print("no alert")
        return False
    except ENIE:
        return False
    except UAP:
        try:
            driver.switch_to.alert.accept()
            return True
        except:
            return False



def 파일이름change(사건번호,의결번호,의결일,사건명,대표조치유형,down_file_name,joinchar="@@"):
    new_name = joinchar.join([의결일.text,의결번호.text,사건번호.text]) + down_file_name
    return new_name
def 무의미한클릭(action,driver):
    element  = driver.find_elements(By.CLASS_NAME, "content")[0]
    action.move_to_element(element).double_click()

def 공정위boxcrawling(driver,pdf파일처리여부 = True):
    def 예외처리(down_file_name):
        if down_file_name in ["2009-06-23@@시권2009-040@@2009특수1282시정권고서(한국사미트).pdf","2009-04-07@@약식2009-094@@2008경규4233의결서 안[중앙일보미디어마케팅(주)(마포은평지점 망원센터)].pdf"]:
            return True
        else:
            return False
    다운_오류 = []
    파일명변경오류 = []
    파일_오류 = []
    시정_약 = []
    시정_나 = []
    나머지 = []
    재결 = []
    for n,tr in enumerate(driver.find_elements_by_css_selector("tr")):
        의결dic, 의결서 = tablerow추출(tr)
        lst = [i.text for i in 의결dic.values()]
        추가dic = {i:k for i,k in zip(의결dic.keys(),lst)}
        if n==0:
            lst.append("filename")
            colnames = lst
        else:
            down_file_name = 의결서.find_element_by_class_name("down_files.pdf").get_attribute("title").split("pdf")[0] + "pdf"
            down_file_name = str예외처리(down_file_name)

            changed = 파일이름change(**의결dic,down_file_name=down_file_name)
            if 예외처리(changed):
                다운_오류.append(changed)
                continue

            기존downed_all = set(map(str예외처리, os.listdir(downpath)))
            #row_data = {c: i for c, i in zip(colnames, lst)}
            while True:
                if is_download_finished(downpath,files = [changed]):
                    break
                else:
                    clicked = 의결서_click(driver, 의결서,n)
                    무의미한클릭(action, driver)

                    #driver.implicitly_wait(imp_time1)
                    #help(driver.implicitly_wait)
                    if clicked:
                        break
            while not is_download_finished(downpath,files = [changed]):
                downed_all = set(map(str예외처리, os.listdir(downpath)))
                down완료 = list(downed_all - 기존downed_all)
                if len(down완료) >= 1 and ".pdf" in down완료[0] and ".crdownload" not in down완료[0]:
                    #downed = is_download_finished(downpath,files = [down_file_name])
                    downed_all = list(map(str예외처리, os.listdir(downpath)))
                    if down완료[0] != down_file_name:
                        down_file_name = down완료[0]
                        changed = 파일이름change(**의결dic, down_file_name=down_file_name)
                    lst.insert(len(lst), changed)
                    break
            while True:
                downed_all = list(map(str예외처리, os.listdir(downpath)))
                #파일이름 바꾸기
                if down_file_name in downed_all:
                    if changed not in downed_all:
                        try:
                            os.rename(os.path.join(downpath, down_file_name), os.path.join(downpath, changed))
                        except:
                            파일명변경오류.append(changed)
                            break
                            #continue
                        downed_all = list(map(str예외처리, os.listdir(downpath)))
                    else:
                        downed_all = list(map(str예외처리, os.listdir(downpath)))
                        break
                if changed in downed_all:
                    break
            if pdf파일처리여부:
                if changed in downed_all:
                    file_pdf = pdf_처리(changed)
                    try:
                        n__, dat = 문서추출(file_pdf,changed)
                        dat.update(추가dic)
                        dat.update({"파일명": changed})
                        if "시정" in n__:
                            if "약관" in n__:
                                시정_약.append(dat)
                            else:
                                시정_나.append(dat)
                        elif n__ == "재결":
                            재결.append(dat)
                        else:
                            나머지.append(dat)
                    except:
                        파일_오류.append(changed)
                        continue
    if pdf파일처리여부:
        오류 = {"다운오류" : 다운_오류,"파일명변경오류" : 파일명변경오류,"파일오류" : 파일_오류}
        return True,시정_약,시정_나,재결,나머지,오류
    else:
        return True
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
def clean_text_blank(file):
    return " ".join(re.split(" {2,}", file)).replace(":","")

def 글자사이공백넣기(글자):
    a = 글자[0]
    for i in 글자[1:]:
        a += r" {0,}" + i
    return a
def mcomp(name_list):
    a = ""
    for i in name_list:
        a +="("
        a += 글자사이공백넣기(i)
        a += ")"
        if i != name_list[-1]:
            a += "|"
    return a
def 문서추출(file,pdf_name):
    def redict만들기(name):
        remat = []
        for i in name:
            if isinstance(i, str):
                if i[:2] == "a_":
                    _ = re.compile(글자사이공백넣기(i[2:])+r" {2,}")
                else:
                    _ = re.compile(글자사이공백넣기(i) + "\s{0,}:{0,}\s{0,}")
            else:
                _ =re.compile(mcomp(i)+" {0,}:{0,} {0,}")
            remat.append(_)
        #remat = [re.compile(글자사이공백넣기(i)+" ?:? ?") if isinstance(i,str) else re.compile(mcomp(i)+" ?:? ?") for i in name]
        rematdict = {}
        for i, j in zip(name, remat):
            if isinstance(i,list):
                rematdict[i[-1]] = j
            else:
                if i[:2] == "a_":
                    i = i[2:]
                rematdict[i] = j
        return rematdict
    def find순서(start,rematdict,file=file):
        end = []
        __name = []
        name_all = list(rematdict.keys())
        for n,k in enumerate(zip(start,name_all)):
            s,matdict = k
            if n == 0:
                try:
                    end.append(s[0])
                    __name.append(matdict)
                except:
                    end
            else:
                if len(s) != 0:
                    if len(s) == 1:
                        if end[-1][-1] <= s[0][0]:
                            end.append(s[0])
                            __name.append(matdict)
                    else:
                        tr = []
                        for seq in s:
                            if end[-1][-1] <= seq[0]:
                                tr.append(seq[0] - end[-1][-1])
                            else:
                                tr.append(500)
                        for n,i in enumerate(tr):
                            if i == min(tr):
                                end.append(s[n])
                                __name.append(matdict)
                else:
                    pass
        return end,__name
    def 페이지1내에있는것확인(file,rematdict):
        if "주문" in rematdict.keys():
            꼭포함 = "주문"
        elif "수락거부시조치" in rematdict.keys():
            for 꼭포함 in ["수락거부시조치","수락여부통지기간","시정기한","적용법조"]:
                try:
                    rematdict[꼭포함].search(file).end()
                except:
                    pass
                else:
                    꼭포함 = 꼭포함
                    break
        else:
            for 꼭포함 in ["적용법조","시정권고이유","시정권고사항"]:
                try:
                    rematdict[꼭포함].search(file).end()
                except:
                    pass
                else:
                    꼭포함 = 꼭포함
                    break
        try:
            최소값 = rematdict[꼭포함].search(file).end()
        except:
            최소값
        page_split = [i.end() for i in re.compile("- {0,}[0-9]{1,} {0,}- {0,}").finditer(file)]
        최소포함page = 0
        for i in page_split:
            if i <=최소값:
                최소포함page +=1
        new_remat = {}
        ls = list(rematdict.items())
        for n,val in enumerate(ls):
            k,i = val
            try:
                if i.search(file) is not None:
                    if i.search(file).end() <= page_split[최소포함page]:
                        new_remat[k] = i
                    else:
                        pass
            except:
                꼭포함
            if n == (len(ls)-1):
                new_remat[k] = i
        return new_remat
    def cleanredict(name,file=file):
        start = []
        rematdict = redict만들기(name)
        rematdict = 페이지1내에있는것확인(file, rematdict)
        for i in rematdict.values():
            start.append([(m.start(0), m.end(0)) for m in i.finditer(file)])
        end,__name = find순서(start,rematdict)
        #a = [file[i[0]:i[1]].replace(" ","") for i in end]
        return __name,end
    file_type = []
    file_type.append(re.compile(글자사이공백넣기("시정권고서")))
    file_type.append(re.compile("의 {0,}결 {0,}(\( {0,}약 {0,}\)) {0,}제 {0,}([0-9]{1,5})"))
    file_type.append(re.compile("의 {0,}결 {0,}(\( {0,}임 {0,}\)) {0,}제 {0,}([0-9]{1,5})"))
    file_type.append(re.compile(글자사이공백넣기("재결제") + r" {0,}([0-9]{1,5})"))
    file_type.append(re.compile(r"결 {0,}정 {0,}(\( {0,}약 {0,}\) {0,}){0,} {0,}제 {0,}([0-9]{1,5})"))
    file_type.append(re.compile(글자사이공백넣기("의결제") + r" {0,}([0-9]{1,5})"))
    #a_붙은 단어는 그 딱 그 단어 자체만 찾음
    시권_약관 = ["시정권고", "사건번호", "사건명", ["피조사인","피청구인", "피심인"],["위피조사인의","위피청구인의","위피심인의"] ,\
          "a_시정권고사항","a_시정권고이유", "a_적용법조"]
    시권_나머지 =["시정권고", "사건번호", "사건명", ["피조사인","피청구인", "피심인"],["위피조사인의","위피청구인의","위피심인의"] ,\
          "a_시정권고사항","법위반내용",["법령의적용","적용법조"],"시정기한","수락여부통지기간" ,["수락거부시의조치","수락거부시조치"]]
    의결_ = ["사건번호", "사건명", ["피조사인", "신청인", "피심인"], "a_원심결", "a_심의종결일", "a_주문", "a_신청취지", "a_이유"]
    page_split = re.compile("- {0,}[0-9] {0,}- {0,}")
    page_one_file = file[:re.compile("- {0,}[0-9]{1,} {0,}- {0,}").search(file).end()]
    for file_name,typ in zip(["시정","약식","임시","재결","결정","의결"],file_type):
        #print(typ.search(file))
        if typ.search(page_one_file) is not None:
            if file_name == "시정":
                file = re.compile("시 {0,}정 {0,}권 {0,}고 {0,}서 {0,}").subn("",file,1)[0]
                시권_typ = re.search(r"[0-9]{2,5}(\w{2})",pdf_name.split("@@")[-1]).group(1)
                if 시권_typ == "약관":
                    name = 시권_약관
                else:
                    name = 시권_나머지
                file_name += 시권_typ
            else:
                name = 의결_
            a,end = cleanredict(name,file)
            data = {}
            data["문서타입"] = file_name
            for n, i in enumerate(end):
                if n != (len(end) - 1):
                    data[clean_text_blank(a[n])] = clean_text_blank(page_split.sub("",file[i[1]:end[n + 1][0]]))
                else:
                    data[clean_text_blank(a[n])] = clean_text_blank(page_split.sub("",file[i[1]:]))
            if len(data) == 0:
                print(data)
            return file_name,data


def 데이터매치check(사건번호,의결번호,의결일):
    re의결일 = re.compile("[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}")
    re의결번호 = re.compile("[\w]{2}[0-9]{4}-[0-9]{3}")
    for t in [사건번호,의결번호,의결일]:
        if re의결번호.match(t.text) is not None:
            new_의결번호 = t
        elif re의결일.match(t.text) is not None:
            new_의결일 = t
        else:
            new_사건번호 = t
    if locals().get("new_의결번호") is None:
        new_의결번호 = 의결번호
    if locals().get("new_의결일") is None:
        new_의결일 = 의결일
    return new_사건번호,new_의결번호,new_의결일


def tablerow추출(tr):
    사건번호,의결번호,의결일 = tr.find_elements_by_class_name("rwd_hidden")
    사건번호,의결번호,의결일 = 데이터매치check(사건번호, 의결번호, 의결일)
    사건명 = tr.find_element_by_class_name("textleft")
    대표조치유형,의결서 = tr.find_elements_by_class_name("dt-nowrap")
    return {"사건번호":사건번호,"의결번호":의결번호,"사건명":사건명,"대표조치유형":대표조치유형,"의결일":의결일},의결서


def 다음페이지로이동(driver,page):
    try:
        driver.find_elements(By.XPATH, f"//*[@id='ltfrList_paginate']/span/a[text()='{page}']")[0].click()
        unt = EC.text_to_be_present_in_element((By.CLASS_NAME,"paginate_button.current"),str(page))
        WebDriverWait(driver, 5).until(unt)
        return True
    except:
        return False
if __name__ =="__main__":
    """
    downed_all = list(map(str예외처리, os.listdir(downpath)))
    시정_약관 = []
    시정_나머지 = []
    재결 = []
    나머지 = []
    for changed in downed_all[6:]:
        file_pdf = pdf_처리(changed)
        n__, dat = 문서추출(file_pdf,changed)
        if "시정" in n__ :
            if "약관" in n__:
                시정_약관.append(dat)
            else:
                시정_나머지.append(dat)
        elif n__ == "재결":
            재결.append(dat)
        else:
            나머지.append(dat)
    나머지_col = ["문서타입", "사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "주문", "심의종결일", "파일명", "이유"]
    재결_col = ["문서타입", "사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "주문", "원심결", "심의종결일", "파일명", "이유"]
    시정_약관_DF_col = ['문서타입','사건번호', '시정권고', '사건명', '시정권고사항','피심인', '적용법조', '시정권고이유', '위피심인의']
    시정_나머지_DF_col = ['문서타입','사건번호','시정권고','사건명','시정권고사항','피심인','적용법조','수락거부시조치', '수락여부통지기간','시정기한','법위반내용', '위피심인의']
    
    시정_약관_DF_ = pd.DataFrame.from_dict(시정_약관).reset_index(drop=True)[시정_약관_DF_col]
    시정_나머지_DF_ = pd.DataFrame.from_dict(시정_나머지).reset_index(drop=True)[시정_나머지_DF_col]
    재결_DF_ = pd.DataFrame.from_dict(재결_DF).reset_index(drop=True)[재결_col].rename(columns={"주문": "세부조치내역"})
    나머지_DF_ = pd.DataFrame.from_dict(나머지_DF).reset_index(drop=True)[나머지_col].rename(columns={"주문": "세부조치내역"})

    changed = "2020-09-25@@결정2020-018@@2018내부0294고발결정서(금호)_최종.pdf"
    file_pdf = pdf_처리(changed)
    n__, dat = 문서추출(file_pdf)
    """
    imp_time1 = 3 #3초 기다림
    imp_time2 = 8 #5초 기다림
    imp_time3 = 5 #5초 기다림

    options = chromeoptionset()
    driver = webdriver.Chrome(r"C:\Users\junlee\Desktop\CODE\Python\chromedriver_ver86.exe",chrome_options=options)
    url = 'https://case.ftc.go.kr/ocp/co/ltfr.do'
    action = ActionChains(driver) #드라이버에 특정 입력 key(action) 전달

    driver.get(url) #url 접속
    driver.implicitly_wait(imp_time1)
    driver.maximize_window()
    #page_num = driver.find_elements_by_class_name("paginate_button.current")[0].text

    down_start_page = 1799
    end_page_num = 1961
    나머지_col = ["문서타입", "사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "주문","원심결","신청취지", "심의종결일", "파일명", "이유"]
    재결_col = ["문서타입", "사건번호", "의결번호", "사건명", "대표조치유형", "의결일", "피심인", "주문", "원심결","신청취지", "심의종결일", "파일명", "이유"]
    시정_약관_DF_col = ['문서타입', '사건번호',"의결번호",'사건명', '시정권고',"의결일", '피심인','시정권고사항', '적용법조',"파일명", '시정권고이유', '위피심인의']
    시정_나머지_DF_col = ['문서타입', '사건번호', "의결번호" ,'사건명',"대표조치유형",'의결일','시정권고','시정권고사항', '피심인','법위반내용' ,'수락거부시조치', '수락여부통지기간', '시정기한','파일명', '법위반내용','위피심인의']

    시정_약관 = []
    시정_나머지 = []
    재결_DF = []
    나머지_DF = []
    오류_all = []
    for i in range(1,end_page_num+1):
        while True:
            페이지이동 = 다음페이지로이동(driver,i)
            if 페이지이동:
                break
        while True:
            if i >= down_start_page:
                if i >= 1269:
                    페이지이동
                다운로드, 시정_약,시정_나,재결,나머지,오류 = 공정위boxcrawling(driver)
                if 다운로드:
                    시정_약관.extend(시정_약)
                    시정_나머지.extend(시정_나)
                    재결_DF.extend(재결)
                    나머지_DF.extend(나머지)
                    오류_all.append(오류)
                    del 나머지,재결,시정_약,시정_나,오류
                    break
            else:
                break

        if (i % 200 == 0)and (i > down_start_page):
            import numpy as np
            나머지_DF_ = pd.DataFrame.from_dict(나머지_DF).reset_index(drop=True)
            나머지_DF_= 나머지_DF_.reindex(columns=나머지_col).rename(columns={"주문": "세부조치내역"})
            나머지_DF_.to_csv(f"의결서_to{i}.csv", encoding="UTF-8")
            del 나머지_DF_
            if len(재결_DF) >0:
                재결_DF_ = pd.DataFrame.from_dict(재결_DF).reset_index(drop=True)
                재결_DF_ = 재결_DF_.reindex(columns=재결_col).rename(columns={"주문": "세부조치내역"})
                재결_DF_.to_csv(f"재결_to{i}.csv", encoding="UTF-8")
                del 재결_DF_
            if len(시정_약관) >0:
                시정_약관_DF_ = pd.DataFrame.from_dict(시정_약관).reset_index(drop=True)
                시정_약관_DF_ = 시정_약관_DF_.reindex(columns=시정_약관_DF_col)
                시정_약관_DF_.to_csv(f"시정_약관_to{i}.csv", encoding="UTF-8")
                del 시정_약관_DF_
            if len(시정_나머지) >0:
                시정_나머지_DF_ = pd.DataFrame.from_dict(시정_나머지).reset_index(drop=True)
                시정_나머지_DF_ = 시정_나머지_DF_.reindex(columns=시정_나머지_DF_col)
                시정_나머지_DF_.to_csv(f"시정_나머지_to{i}.csv", encoding="UTF-8")
                del 시정_나머지_DF_
            시정_약관 = []
            시정_나머지 = []
            재결_DF = []
            나머지_DF = []
    import pickle

    with open(f'오류.pickle', 'wb') as handle:
        pickle.dump(오류_all, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #나머지_DF_["문서타입"].drop_duplicates()
    #재결_DF_["문서타입"].drop_duplicates()
    #572 page 까지 완료

"""
#pdf 추출 check 용 코드

changed = "2020-09-10@@의결2020-259@@2018안정34785. 의결서(굿럭 경고심의요청).pdf"
downed_all = list(map(str예외처리, os.listdir(downpath)))
    시정 = []
    나머지 = []
    for changed in downed_all:
        file_pdf = pdf_처리(changed)
        n__,dat = 문서추출(file_pdf)
        if n__ == "시정":
            시정.append(dat)
        else:
            나머지.append(dat)
        #타입, 항목, redict = 문서타입(앞부분_pdf)
        # TODO 다음 인덱싱 한 항목의 길이가 일정 범위 이상 길 경우 pop하고 그 종목제외하고 다시 iteration 하기
        #data = 세부조치내역(file_pdf, 항목, redict)
        #print(data)
    시정 = pd.DataFrame.from_dict(시정)
    나머지 = pd.DataFrame.from_dict(나머지)
    DF = DF[["사건명","사건번호","피심인","피조사인","신청인","신청취지","심의종결일","원심결","주문","이유"]]

"""
"""
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "myDynamicElement"))
    )

except:
  pass
else:


finally:
  driver.quit()

def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script('''
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        ''')
paths = WebDriverWait(driver, 120, 1).until(every_downloads_chrome)
print(paths)
help(WebDriverWait)



"""


