from flask import Flask, render_template, request, jsonify
from bson.objectid import ObjectId
from pymongo import MongoClient
import json
from bs4 import BeautifulSoup
import requests
client = MongoClient("mongodb+srv://dib3474:1q2w3e4r@cluster0.lurm5gz.mongodb.net/?retryWrites=true&w=majority")
db = client.wetoon

app = Flask(__name__)


@app.route('/', methods=["GET"])
def home():
    return render_template("index.html")

# index.html 렌더
@app.route('/archive', methods=["GET"])
def render_index():
    return render_template("index.html")

# 내가 본 웹툰 목록 불러오기
@app.route("/api/archive", methods=["GET"])
def read_card_data():
    contents = list(db.webtoons.find({}))
    for content in contents:
        content['_id'] = str(content['_id'])
    return jsonify({"result": contents})

# 내가 본 웹툰 추가하기
@app.route('/api/archive', methods=["POST"])
def add_card_data():
    title_receive = request.form["title_give"]
    reason_receive = request.form["reason_give"]
    writer_receive = request.form["writer_give"]
    
    url_receive = f"https://korea-webtoon-api.herokuapp.com/search?keyword={title_receive}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = json.loads(data.text)
    webtoon = soup['webtoons'][0]
    
    title_receive = webtoon['title']
    img_url = webtoon['img']
    link = webtoon['url']

    doc = {
        'img_url': img_url,
        'link': link,
        'title': title_receive,
        'reason': reason_receive,
        'writer': writer_receive,
    }
    db.webtoons.insert_one(doc)
    return jsonify({"msg": "등록 완료!"})

# 내가 본 웹툰 수정하기
@app.route('/api/archive/update/<card_id>', methods=["POST"])
def update_card_data(card_id):
    card_id = ObjectId(card_id)
    reason_receive = request.form["reason_give"]
    writer_receive = request.form["writer_give"]
    db.webtoons.update_one({'_id': card_id}, {'$set': {'reason': reason_receive, 'writer': writer_receive, }})
    return jsonify({"msg": "수정 완료"})

# 내가 본 웹툰 삭제하기
@app.route('/api/archive/delete/<card_id>', methods=["POST"])
def delete_card_data(card_id):
    id_receive = ObjectId(card_id)
    db.webtoons.delete_one({'_id': id_receive})
    return jsonify({"msg": "삭제 완료"})

@app.route('/api/archive/ranking/naver', methods=["GET"])
def ranking_naver_data():
    url_receive = "https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&mra=bjQz&pkid=47&qvt=0&query=%EC%A3%BC%EA%B0%84%20%EB%9E%AD%ED%82%B9%20%EC%9B%B9%ED%88%B0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, "html.parser")
    
    webtoons = soup.select('.list_image_info > ul > li')
    
    contents = []
    
    for i, webtoon in enumerate(webtoons):
        title = webtoon.select_one('.name').text
        img = webtoon.select_one('img')['src']
        webtoon_id = img.split("%2F")[5]
        url = f"https://comic.naver.com/webtoon/list?titleId={webtoon_id}"
        content = {
            'ranking': i+1,
            'title': title,
            'img_url': img,
            'link': url,
        }
        contents.append(content)
    return jsonify({"result": contents})

@app.route('/api/archive/ranking/kakao', methods=["GET"])
def ranking_kakao_data():
    url_receive = "https://page.kakao.com/landing/ranking/10"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, "html.parser")
    
    webtoons = soup.select('.grid')[1].find_all("div", recursive=False)[:15]
    
    contents = []
    for i, webtoon in enumerate(webtoons):
        data = json.loads(webtoon.select_one('a > div')['data-t-obj'])
        title = data['eventMeta']['name']
        img = webtoon.select_one('img')['src']
        webtoon_id = data['eventMeta']['id']
        url = f"https://page.kakao.com/content/{webtoon_id}"
        content = {
            'ranking': i+1,
            'title': title,
            'img_url': img,
            'link': url,
        }
        contents.append(content)
    return jsonify({"result": contents})

if __name__ == "__main__":
    app.run()
