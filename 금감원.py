from 공정위 import *
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
def key누르고항목뜰때까지기다리기(driver,target_path,complete_signal_path,visible=True):
    try:
        with suppress(ENIE):
            driver.find_element_by_xpath(target_path).click()
        # 의결서.find_element_by_class_name("down_files.pdf").click()
        if visible:
            element = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH,complete_signal_path)))
        else:
            element = WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(
                (By.XPATH, complete_signal_path)))
        print("pass")
        #if action is not None:
        #    pass
        #elif action == "click":
        return True
    except TimeoutException:
        print("no pass")
        return False
def page_정보만들기(driver,page):
    url = f"http://www.fss.or.kr/fss/kr/promo/bodobbs_list.jsp?EndDate=&y=0&s_kind=title&StartDate=&s_title=%B0%A8%B8%AE&x=0&page={page}"
    driver.get(url)  # url 접속
    driver.implicitly_wait(imp_time1)
    table = driver.find_element_by_xpath("//*[@id='contents_area']/div[2]/table").find_elements_by_css_selector("tr")
    col = [i.text for n,i in enumerate(table[0].find_elements_by_css_selector("th"))]
    data = []
    for j in range(1, len(table)):
        tr = table[j]
        data.append([i.text  for i in tr.find_elements_by_css_selector("td")])
        td = tr.find_elements_by_css_selector("td")[4]
        a = td.find_element_by_css_selector("a")
        if "새창으로 이동" in a.get_attribute("title"):
            a.click()
            """
            while True:
                try:
                    element = WebDriverWait(td, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "fileAdd")))
                    WebDriverWait(td, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "fileAdd")))
                except TimeoutException:
                    pass
                else:

                    break
            """
            driver.implicitly_wait(0.3)
            li = td.find_element_by_class_name("fileAdd").find_elements_by_css_selector("li")
            for i in range(len(li)):
                if ".hwp" in li[i].text:
                    num = i
            li[num].find_element_by_css_selector("a").click()
            data[j - 1][4] = li[num].text
            a.click()
        else:
            a.click()
            data[j-1][4] = a.get_attribute("title")
    return pd.DataFrame(data,columns = col)

if __name__ == "__main__":
    options = chromeoptionset()
    url = "http://www.fss.or.kr/fss/kr/promo/bodobbs_list.jsp?EndDate=&StartDate=&s_kind=title&y=0&s_title=%B0%A8%B8%AE&x=0&page=31"

    driver = webdriver.Chrome(origin_path + "/chromedriver_ver86.exe", chrome_options=options)
    action = ActionChains(driver) #드라이버에 특정 입력 key(action) 전달
    driver.get(url) #url 접속
    driver.implicitly_wait(imp_time1)
    driver.maximize_window()
    DF = []
    for i in range(1,36):
        DF.append(page_정보만들기(driver,i))
    #driver.find_elements_by_xpath("//*[@id='contents_area']/div[2]/table")
    df = pd.concat(DF)
    df = df.set_index("번호")
    df.to_excel("금감원사이트_정리.xlsx")

    hwp_files = os.listdir("금감원_file")
    if olefile.isOleFile(파일명):
        f = olefile.OleFileIO(파일명)
        encoded_text = f.openstream('PrvText').read()
        decoded_text = encoded_text.decode('UTF-16')
    else:
        pass






