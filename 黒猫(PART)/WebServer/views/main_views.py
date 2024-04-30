"""
@main_views.py
@brief 이 파일은 데이터 블루프린트에 대한 라우트와 함수들을 포함하고 있습니다.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from WebServer import db
from sqlalchemy import text
from flask import Flask, Response
import numpy as np
import cv2
from mss import mss
from PIL import Image
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(grandparent_dir)
from Source.SERVICE import *

bp = Blueprint('data', __name__, template_folder='templates', url_prefix="/")

# /**
#  * @brief 화면을 캡처하고 JPEG 이미지로 프레임을 생성합니다.
#  * @param monitor_index 캡처할 모니터의 인덱스.
#  * @return JPEG 이미지로 프레임을 생성하는 제너레이터.
#  */
def capture_screen(monitor_index):
    with mss() as sct:
        monitor = sct.monitors[monitor_index]
        while True:
            screen = sct.grab(monitor)
            img = Image.frombytes('RGB', (screen.width, screen.height), screen.rgb)
            img_np = np.array(img)
            frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            
# =================================================================================      
# /**
#  * @brief 인덱스 라우트.
#  * @return 렌더링된 index.html 템플릿.
#  */      
@bp.route('/')
def index():
    
    return render_template('index.html')

#/**
# * @brief 데이터베이스 테이블의 내용을 보여줍니다.
# * @param table 표시할 테이블의 이름.
# * @return 테이블 내용이 포함된 렌더링된 database.html 템플릿.
# */
@bp.route('/database/<table>' , methods=['GET','POST'])
def show_database(table):
    req_dict = request.form.to_dict() # 값들 갖고 오기 
    input_text = req_dict.get('query')
    if input_text :
        result = db.session.execute(text(f'SELECT * FROM {table} where Q like "%{input_text}%"'))
    else:
        result = db.session.execute(text(f'SELECT * FROM {table}'))
    rows = [row for row in result]
    return render_template('database.html', rows=rows, table=table)

#/**
# * @brief screen_feed.html 템플릿을 렌더링합니다.
# * @return 렌더링된 screen_feed.html 템플릿.
# */
@bp.route('/screen_feed')
def screen_feed():
    #Service()
    return render_template('screen_feed.html')

#/**
# * @brief 캡처된 화면을 비디오 피드로 스트리밍합니다.
# * @return 비디오 피드가 포함된 응답.
# */
@bp.route('/video_feed')
def video_feed():
    return Response(capture_screen(1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#/**
# * @brief 서비스를 시작하고 결과가 포함된 screen_feed.html 템플릿을 렌더링합니다.
# * @return 서비스 결과가 포함된 렌더링된 screen_feed.html 템플릿.
# */
@bp.route('/screen_feed/service')
def service_start():
    value = Service()
    if value == 2 or value==1:
        return f"정해진 규칙을 읽을 수 없습니다"
    OX, OQ, NQ, Genre, Nominee, answer = value
    return render_template('screen_feed.html', OX=OX, OQ=OQ, NQ=NQ, Genre=Genre, Nominee=Nominee, answer=answer)


#/**
# * @brief 주어진 질문에 해당하는 행을 지정된 테이블에서 삭제합니다.
# * @param table 테이블의 이름.
# * @param Question 삭제할 행을 찾기 위한 질문.
# * @return 지정된 테이블에 대한 show_database 라우트로 리다이렉트.
# */
@bp.route('/delete_db/<table>_<Question>')
def delete_db(table, Question):
    db.session.execute(text(f'DELETE FROM {table} WHERE Q like "%{Question}%"'))
    db.session.commit()
    return redirect(url_for('data.show_database', table=table))

#/**
# * @brief 주어진 질문에 해당하는 행을 지정된 테이블에서 검색하여 업데이트를 위해 가져옵니다.
# * @param table 테이블의 이름.
# * @param Question 검색할 행을 찾기 위한 질문.
# * @return 검색된 행이 포함된 렌더링된 update.html 템플릿.
# */
@bp.route('/update_db/<table>_<Question>')
def update_db(table, Question):
    result=db.session.execute(text(f'select * FROM {table} WHERE Q like "%{Question}%"'))
    rows = [row for row in result]
    return render_template('update.html', rows=[rows[0]], table=table)


#/**
# * @brief 폼 데이터를 기반으로 지정된 테이블의 행을 업데이트합니다.
# * @param table 테이블의 이름.
# * @return 지정된 테이블에 대한 show_database 라우트로 리다이렉트.
# */
@bp.route('/submit_form/<table>', methods=['GET','POST'])
def update_complete(table):
    req_dict = request.form.to_dict()
    hidden_id = req_dict.get('hidden_id')
    Q = req_dict.get('Q')
    K1 = req_dict.get('K1')
    K2 = req_dict.get('K2')
    K3 = req_dict.get('K3')
    K4 = req_dict.get('K4')
    A = req_dict.get('A')    
    db.session.execute(text(f"""UPDATE {table}
SET 
    Q = '{Q}',
    K1 = '{K1}',
    K2 = '{K2}',
    K3 = '{K3}',
    K4 = '{K4}',
    A = '{A}'
WHERE
    Q like '%{hidden_id}%';
"""))
    db.session.commit()
    return redirect(url_for('data.show_database', table=table))


#/**
# * @brief 새로운 행을 지정된 테이블에 삽입합니다.
# * @return 삽입된 행이 포함된 렌더링된 database.html 템플릿.
# */
@bp.route('/insert_db', methods=['GET','POST'])
def insert():
    req_dict = request.form.to_dict()
    Q = req_dict.get('Q')
    K1 = req_dict.get('K1')
    K2 = req_dict.get('K2')
    K3 = req_dict.get('K3')
    K4 = req_dict.get('K4')
    A = req_dict.get('A') 
    Genre = req_dict.get('Genre')
    db.session.execute(text(f"""INSERT INTO {Genre} VALUES ('{Q}','{Genre}','{K1}','{K2}','{K3}','{K4}','{A}')"""))
    db.session.commit()
    result = db.session.execute(text(f'SELECT * FROM {Genre}'))
    rows = [row for row in result]
    return render_template('database.html', rows=rows, table=Genre)