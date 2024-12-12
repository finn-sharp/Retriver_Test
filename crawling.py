from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options

# 클릭 수행을 위해 명시적 대기 설정
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import tqdm
import time
import re



def data_preprocessing(data, url):
    patterns = {
        '공고명': r"공고명\s+([^\n]+)",
        '기관명': r"기관명\s(([^\n]+)(?= 조회 \d+))",
        '마감일': r"마감일\s([0-9]{4}-[0-9]{2}-[0-9]{2})",
        '채용직급': r"채용직급\s([^\n]+)",
        '근무지역': r"근무지\s([^\n]+)",
        '장애인 채용 / 우대': r"장애인 채용 / 우대\s([^\n]+)",
        '본문' : r"첨부파일[\s\S]+"
    }

    # 각 항목을 정규 표현식으로 추출
    extracted_data = {}

    # 링크를 클립보드에서 가져오기
    extracted_data['링크'] = url

    for key, pattern in patterns.items():
        match = re.search(pattern, data)
        if match:
            if key == '본문':
                clean_text = " ".join(match.group(0).split())  # 개행 문자를 제거하고 공백으로 합침
                extracted_data[key] = clean_text        
            else:
                extracted_data[key] = match.group(1)

    return extracted_data


# 데이터 추출
def scrap_data(No, driver):
    time.sleep(1)
    page_idx = 241111+No
    url = f"https://www.gojobs.go.kr/apmView.do?empmnsn={page_idx}&selMenuNo=400&menuNo=401&upperMenuNo="
    driver.get(url)

    # 자바스크립트 동작을 기다리기 위해 시간 대기 (예시)
    time.sleep(2)

    # #apmViewTbl 요소를 찾고, 그 안의 데이터를 추출
    apmViewTbl = driver.find_element(By.ID, "apmViewTbl")
    
    # 링크 추출을 위한 공유 버튼 클릭
    # 이미지 클릭을 위한 대기
    image_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#viewForm > div.clear_after.mt30 > button:nth-child(1) > img"))
    )
    image_element.click()
    
    try:
        alert = Alert(driver)
        alert.accept()  # 알림 확인을 클릭하여 닫음
    except:
        print("알림이 없습니다.")
    
    # 링크 정보는 클립보드에 저장되어있음
    job_data = data_preprocessing(apmViewTbl.text, url)

    return job_data

# 추출된 항목 정리
def fn_crawling(No):
    # 크롬 드라이버 자동으로 다운로드하고 설치
    service = Service(ChromeDriverManager().install())

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 헤드리스 모드로 실행
    chrome_options.add_argument("--no-sandbox")  # 보안 모드 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # 메모리 부족 문제 해결
    chrome_options.add_argument("--remote-debugging-port=9223")  # 원격 디버깅 포트 설정
    # chrome_options.add_argument("--disable-gpu")  # GPU 비활성화

    # Chrome 브라우저 실행
    driver = webdriver.Chrome(service=service, options=chrome_options)

    data = []
    for No_page in tqdm.tqdm(range(No)):
        try :
            data.append(scrap_data(No_page, driver))
            time.sleep(1)
        except :
            pass
    
    # 브라우저 종료
    driver.quit()
    return data


if __name__=='__main__' :
    No = int(input("수집할 데이터의 개수를 자연수로 입력하세요 : "))
    print(f'::: {No}개의 구인 데이터 수집 시작')
    data = fn_crawling(No)
    data = pd.DataFrame(data)
    data.to_csv('nara_jobdata.csv')
    print(f'::: {No}개의 구인 데이터 수집 완료')