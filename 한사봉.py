from private import id_,pw_
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from bs4 import BeautifulSoup
from hyperparam import *
from win32control import *
def chromeoptionset():
    # option 추가 할거 있으면 여기 하기
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument("disable-gpu")
    options.add_argument("lang=ko_KR")  # 한국어!
    # options.add_argument("proxy-server=localhost:8080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    options.add_experimental_option("prefs", {
        # "download.default_directory": down_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,
        'profile.default_content_setting_values.automatic_downloads': 1
    })
    return options
def table_parser(tb):
    data = []
    templen = len(tb.find_all("tr"))
    for i in range(templen -1):
        tempTr = tb.find_all("tr")[i]
        if i == 0:
            col = [i.contents[0] for i in tempTr.find_all("th")]
        else:
            row = []
            for j in range(len(col)):
                tempTd = tempTr.find_all("td")[j].text
                row.append(tempTd)
            data.append(row)
    return pd.DataFrame(data,columns=col)
def page이동(num):
    while True:
        try:
            now_page = int(driver.find_element_by_css_selector("tfoot").find_element_by_class_name("numberLink").find_element_by_class_name("strong").text)
        except:
            무의미한클릭()
        else:
            break
    if num > 10:
        if now_page <= 10:
            while True:
                try:
                    driver.find_element_by_css_selector("tfoot").find_element_by_id("pagingPanel").find_element_by_xpath("""//*[@id="pagingPanel"]/a[2]""").click()
                except:
                    무의미한클릭()
                else:
                    break
            #unt = EC.text_to_be_present_in_element((By.CLASS_NAME, "strong"), str(11))
            #WebDriverWait(driver, 5).until(unt)
    else:
        if now_page > 10:
            while True:
                try:
                    driver.find_element_by_css_selector("tfoot").find_element_by_id("pagingPanel").find_element_by_xpath("""//*[@id="pagingPanel"]/a[2]""").click()
                except:
                    무의미한클릭()
                else:
                    break
    while True:
        try:
            anchor = driver.find_element_by_css_selector("tfoot").find_element_by_class_name("numberLink").find_elements_by_css_selector("a")
            anchor = [i for i in anchor if i.text == str(num)]
            if len(anchor) != 0:
                if anchor[0].is_enabled():
                    anchor[0].click()
            else:
                return
        except:
            무의미한클릭()
            #print(f"{num} page 진입 실패")
        else:
            break


options = chromeoptionset()
url = 'https://portal.hanyang.ac.kr/sugang/'


driver = webdriver.Chrome(origin_path + "/chromedriver.exe", chrome_options=options)
action = ActionChains(driver) #드라이버에 특정 입력 key(action) 전달

driver.get(url) #url 접속
driver.implicitly_wait(imp_time1)
driver.maximize_window()
driver.find_element_by_xpath("//*[@id='btn-user2']").click()
driver.implicitly_wait(imp_time1)
#print(driver.window_handles)
driver.switch_to.window(driver.window_handles[-1])
action = ActionChains(driver)
action.send_keys(id_,Keys.TAB,pw_,Keys.ENTER).perform()
driver.switch_to.window(driver.window_handles[0])
#driver.implicitly_wait(imp_time1)
time.sleep(imp_time1)
driver.find_element_by_xpath("//*[@id='snb']/ul/li[12]/a").click()  #사회봉사 탭 클릭
driver.find_element_by_xpath("""//*[@id="M010392"]/a""").click()    #사회봉사 수강신청 탭 클릭
time.sleep(imp_time1)
ActionChains(driver).send_keys(Keys.ESCAPE).perform()               #이상한거 뜨는거 벗어나기
def 무의미한클릭():
    element  = driver.find_elements(By.ID,'container')[0]
    ActionChains(driver).move_to_element(element).double_click()
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
def 다시돌아가기():
    driver.find_element_by_xpath("""//*[@id="btn_back"]""").click()

while True:
    while True:
        try:
            driver.find_element_by_xpath("""//*[@id="btn_find"]""").click()
        except:
            time.sleep(1.5)
            무의미한클릭()
        else:
            break
    for i in range(1,17):
        page이동(i)
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'lxml')
        tb = soup.select("table")[0]
        t = table_parser(tb)
        should_click = t.loc[(t["제한인원"] > t["신청인원"]) & (t["프로그램명"].apply(lambda x: True if "사전선발" not in x else False))].index.to_list()
        print(t[["프로그램명","제한인원","신청인원"]])
        if len(should_click) > 0:
            for can_click_ in should_click:
                driver.find_element_by_xpath(
                    f"""/html/body/div[2]/div/div[2]/div/form/div/div[1]/div[3]/table/tbody/tr[{can_click_ + 1}]/td[1]/span/input""").click()  # 신청버튼 클릭
                driver.implicitly_wait(imp_time1)
                driver.find_element_by_xpath("""//*[@id="sincheongGyoyukSeq"]""").click()  # 소양교육일 선택
                ActionChains(driver).send_keys(Keys.DOWN, Keys.ENTER).perform()  # 소양교육일 일자 선택
                driver.find_element_by_xpath("""//*[@id="btn_confirm"]""").click()  # 신청버튼 클릭
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                다시돌아가기()



