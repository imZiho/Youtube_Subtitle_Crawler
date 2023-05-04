from selenium import webdriver                                    
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service                  
import time
import random

from youtube_transcript_api import YouTubeTranscriptApi

import os
import shutil

def scroll():                                                         # 무한 스크롤 함수이용
    try:        
        # 페이지 내 스크롤 높이 받아오기
        last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            # 임의의 페이지 로딩 시간 설정
            # PC환경에 따라 로딩시간 최적화를 통해 scraping 시간 단축 가능
            pause_time = random.uniform(1, 2)
            # 페이지 최하단까지 스크롤
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            # 페이지 로딩 대기
            time.sleep(pause_time)
            # 무한 스크롤 동작을 위해 살짝 위로 스크롤(i.e., 페이지를 위로 올렸다가 내리는 제스쳐)
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight-50)")
            time.sleep(pause_time)
            # 페이지 내 스크롤 높이 새롭게 받아오기
            new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
            # 스크롤을 완료한 경우(더이상 페이지 높이 변화가 없는 경우)
            if new_page_height == last_page_height:
                print("스크롤 완료")
                break
            # 스크롤 완료하지 않은 경우, 최하단까지 스크롤
            else:
                last_page_height = new_page_height
            
    except Exception as e:
        print("에러 발생: ", e)


service = Service(ChromeDriverManager().install())

# chrome dirver option 설정 
options = webdriver.ChromeOptions()

# chrome 화면 띄우지 않기
options.add_argument('--headless')

#driver 설정
driver = webdriver.Chrome(service=service, chrome_options=options)

# 스크래핑 할 URL 세팅
URL = "https://www.youtube.com/?gl=kr"

# 크롬 드라이버를 통해 지정한 URL의 웹 페이지 오픈
driver.get(URL)

# 웹 페이지 로딩 대기
time.sleep(3)

# 무한 스크롤 함수 실행
#scroll()

html_source = driver.page_source
soup_source = BeautifulSoup(html_source, 'html.parser')
content_total = soup_source.find_all(class_ = 'yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media')

# 콘텐츠 링크만 추출
content_total_link = list(map(lambda data: data["href"].replace('/watch?v=',""), content_total))
# 콘텐츠 제목만 추출
content_total_title = list(map(lambda data: data.get_text().replace("\n", ""), content_total))

print(content_total_link)                                                   

# subtitles 폴더 존재 유무 확인 후 subtitles 폴더 생성
if os.path.isdir("subtitles") == True:      
    shutil.rmtree("subtitles")              
    os.mkdir("subtitles")
if os.path.isdir("subtitles") == False:
    os.mkdir("subtitles")

for i in range(len(content_total_link)):                                    
    # 해당 영상의 자막 자체가 존재할 경우 try문 실행
    try:
        # 각 영상의 사용 가능한 자막에 대한 정보 변수에 저장
        transcript_list = YouTubeTranscriptApi.list_transcripts(content_total_link[i])

        # 자막의 언어 코드와 해당 언어 자막의 자동생성 여부를 저장할 객체 생성  
        language_dic = {}                                                     
        for transcript in transcript_list:
            language_dic[transcript.language_code]=transcript.is_generated

        # 한국어 자동생성 자막일 경우 자막 추출
        if language_dic.get('ko',False)==True:
            # get_transcript 함수를 사용하여 해당 영상의 자막에 관한 데이터를 크롤링 해온 후 변수에 저장                             
            subtitle = YouTubeTranscriptApi.get_transcript(content_total_link[i], languages=['ko'])    

            # 해당 영상의 제목으로 텍스트 파일 생성 및 인코딩 언어 설정                                                                                 
            with open(f'subtitles/{content_total_title[i]}.txt', "w", encoding='utf-8') as f:
                # srt내의 자막을 text파일에 작성
                for i in range(len(subtitle)):                                        
                    f.write(f"{subtitle[i]['text']}\n") 

        # 해당영상의 한국어 자동생성 자막이 아닐 경우 다음 영상 링크 확인
        else:                                                           
            continue
    # 해당 영상의 자막 자체가 존재하지 않을 경우 다음 영상 링크 확인
    except:                                                              
        continue                                                        


# reference : https://github.com/park-gb/youtube-content-scaper
