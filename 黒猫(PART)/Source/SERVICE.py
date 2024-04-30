import pandas as pd
from Korpora import Korpora
from konlpy.tag import Okt
# 일본어 tokenize import
from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from joblib import dump
from joblib import load
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pyautogui
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(current_dir)
from CRAWL import *

print(current_dir)

Genre_list = ['雑学', 'スポーツ', '理系', '芸能', 'アニメゲーム', '文系']
# Genre 내용을 사용하여 모델 변수 6개를 만들고, 모델 불러오기
雑学= load('Model/sim_雑学.joblib')
スポーツ = load('Model/sim_スポーツ.joblib')
理系 = load('Model/sim_理系.joblib')
芸能 = load('Model/sim_芸能.joblib')
アニメゲーム = load('Model/sim_アニメゲーム.joblib')
文系 = load('Model/sim_文系.joblib')
Genre_model = [雑学, スポーツ, 理系, 芸能, アニメゲーム, 文系]

flag=0 # 데이터 추가 변수
# 화면 클릭 함수
def click_answer(most_similar_index):
    if most_similar_index==0 :
        pyautogui.click(950, 980)  
    elif most_similar_index==1:
        pyautogui.click(950, 1110) 
    elif most_similar_index==2:
        pyautogui.click(950, 1244)
    elif most_similar_index==3:
        pyautogui.click(950, 1363) 
        
def find_answer_location(imgpath):
    screenshot = np.array(pyautogui.screenshot())# 전체화면 캡처
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) # O.png탐색
    result = cv2.matchTemplate(gray, cv2.imread(imgpath, 0), cv2.TM_CCOEFF_NORMED)# 이미지 검출
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)# 최대값 찾기
    return max_loc     # 최대값 위치 반환

# 정답 찾기
def find_answer():
    # 1초동안 실행하기
    for _ in range(5) :
        x,y = find_answer_location('Img/XX.png')
        if 1050<=x<=1150 and 600<=y<=700:
            x,y = find_answer_location('Img/O.png')
            if 940<=x<=1050 and 970<=y<=1094:
                return 1
            if 940<=x<=1050 and 1100<=y<=1210:
                return 2
            if 940<=x<=1050 and 1234<=y<=1341:
                return 3
            if 940<=x<=1050 and 1353<=y<=1484:
                return 4
        time.sleep(0.1)
    return 0

def levenshtein_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

    return dp[m][n]


def Service():    
    mismatch = pd.read_csv('Source/data.csv')
    # 문제 맞추기 시작

    txt_list = capture_screen()
    if len(txt_list)<5:
        print("선지가 없습니다.")
        return 1
    Question, Genre, Nominee = extract(txt_list)
    if Genre=="だっ" : Genre="雑学"
    if Genre==" アニメゲがゲーム" : Genre="アニメゲーム"
    if Genre=="茎能" : Genre="芸能"

    try :
        model_index= Genre_list.index(Genre)
    except:
        print("타이밍에 맞지 않게 스캔하여 장르 인식 불가")
        return 2
    model = Genre_model[model_index]
    df = pd.read_csv(f"Data/{Genre}.csv",usecols =["Q","K1","K2","K3","K4","A"])
    # 각 열을 문자열로 합쳐서 튜플 리스트 생성
    QnA = [(q + ":" + k1 +","+ k2 +","+ k3 +","+ k4, index, a) for index, q, k1, k2, k3, k4, a in zip(df.index, df['Q'], df['K1'], df['K2'], df['K3'], df['K4'], df["A"])]

    # 입력 문장을 예측
    input_text =",".join((Question, Nominee[0], Nominee[1], Nominee[2], Nominee[3]))
    predicted_label = model.predict([input_text])[0]
    
    print(f"{'='*50}\n1.{QnA[predicted_label][0]}")
    print(f"2.{Question}\n{'='*50}")
    
    # 예측된 레이블에 해당하는 질문 가져오기
    predicted_question = QnA[predicted_label][2]

    if QnA[predicted_label][2] in Nominee:
        most_similar_index = Nominee.index(QnA[predicted_label][2])
    else :
        # 문장 벡터화
        try:
            distances = [levenshtein_distance(predicted_question, text) for text in Nominee]

            # 가장 유사한 단어 추출
            most_similar_index = distances.index(min(distances))
            print("➡️Vectorization : ",[predicted_question] + [nominee for nominee in Nominee])

        except:
            most_similar_index = 0

    # 결과 출력 & 클릭
    print("정답 :", most_similar_index,"🤩")
    click_answer(most_similar_index)
    answer_num=find_answer()
    answer=Nominee[answer_num-1]
    if answer_num : # 문제를 틀렸다면
        return "오답", QnA[predicted_label][0], Question, Genre, Nominee, answer
        
    else : 
        return "정답", QnA[predicted_label][0], Question, Genre, Nominee, answer
    
if __name__=='__main__':
    Service()