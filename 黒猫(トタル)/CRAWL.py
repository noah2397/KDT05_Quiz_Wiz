import cv2
import pytesseract
import pyautogui
import numpy as np
import openai
from openai import OpenAI

coordinate_list=[[880,667,1600,719], # 문제(전체화면, 광고X) 1번째 줄
                 [880,710,1600, 760], # 문제(전체화면, 광고X) 2번째 줄
                 [880,760,1600,808], # 문제(전체화면, 광고X) 3번째 줄
                 [975,1010,1600,1063], # 선지1
                 [975,1130,1574,1187], # 선지2
                 [975,1254,1574,1316], # 선지3
                 [975,1387,1574,1447]] # 선지4

def capture_screen():
    txt=[]
    screenshot = np.array(pyautogui.screenshot())
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))

    for index, (x1, y1, x2, y2) in enumerate(coordinate_list):
        cropped_screen = screenshot[y1:y2, x1:x2]
        cropped_screen = cv2.cvtColor(cropped_screen, cv2.COLOR_BGR2GRAY)
        t, cropped_screen = cv2.threshold(cropped_screen, -1, 255,  cv2.THRESH_BINARY | cv2.THRESH_OTSU) 
        cropped_screen = cv2.bilateralFilter(cropped_screen, 5, 75, 75)
        cropped_screen = cv2.resize(cropped_screen, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)


        cropped_screen = cv2.erode(cropped_screen, k)
        if False:
            cv2.imshow("ex",cropped_screen)
            cv2.waitKey()
            cv2.destroyAllWindows()
        if t >= 80: # 빈 값이면 거르기 
            txt.append(pytesseract.image_to_string(cropped_screen, lang='jpn', config='--psm 6 --oem 1'))
    return txt

def extract(txt_list):
    # txt_list에 있는 각각의 요소에 "\n\x0c"를 떼서 문자열로 만들기
    cleaned_data = [element.replace('\n\x0c', '') for element in txt_list]
    Question, Nominee="",[]
    for i in range(len(cleaned_data)):
        if i < len(cleaned_data)-4:
            Question=Question+cleaned_data[i]
        else:
            Nominee.append(cleaned_data[i])
    return Question, Nominee

# 정답과 오답을 찾는 함수 만들기
# 캡쳐화면에 O.png가 있는 위치를 x,y로 반환하기
import time 

def find_answer_location():
    screenshot = np.array(pyautogui.screenshot())# 전체화면 캡처
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY) # O.png탐색
    result = cv2.matchTemplate(gray, cv2.imread('O.png', 0), cv2.TM_CCOEFF_NORMED)# 이미지 검출
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)# 최대값 찾기
    return max_loc     # 최대값 위치 반환

# 정답 찾기
def find_answer():
    while True :
        x,y = find_answer_location()
        if 940<=x<=1050 and 970<=y<=1094:
            return 1
        if 940<=x<=1050 and 1100<=y<=1210:
            return 2
        if 940<=x<=1050 and 1234<=y<=1341:
            return 3
        if 940<=x<=1050 and 1353<=y<=1484:
            return 4

#answer_num=find_answer()




