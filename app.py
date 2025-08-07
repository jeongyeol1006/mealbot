from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import urllib3

app = Flask(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_day_offset(offset):
    return (datetime.today() + timedelta(days=offset)).day

def yo_il(o_nul):
    return (datetime.today() + timedelta(days=o_nul)).weekday()

def yoil_count(target_weekday):
    today_weekday = datetime.today().weekday()
    days_until = (target_weekday - today_weekday + 7) % 7
    if days_until == 0:
        days_until = 7
    return days_until

def get_school_meal(url, day=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('title').text.strip()
        school_name = re.sub(r'급식 메뉴 조회 서비스', '', title)

        rows = soup.find_all('tr')
        if day is None:
            day = datetime.today().day

        result = ""
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 2:
                date_text = re.sub(r'[^0-9]', '', cells[0].text.strip())
                if date_text and int(date_text) == int(day):
                    meal = ''.join([
                        f"• {item.previous_sibling.strip()}\n"
                        for item in cells[2].find_all('br') if item.previous_sibling
                    ])
                    result += f"[{school_name.strip()}]\n📅 {cells[0].text.strip()} ({cells[1].text.strip()})\n🍱 급식 메뉴:\n {meal}"
                    break

        if not result:
            result = f"🕵️‍♂️ {day}일 급식 정보가 등록되어 있지 않거나 아직 업데이트되지 않았어요.\n학교 홈페이지를 확인해보세요."

        return result

    except Exception as e:
        return f"🚨 오류 발생: {str(e)}"

@app.route('/')
def index():
    return render_template('chat.html')  # chat.html 템플릿 필요


@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message').strip().lower()
    school_url = "https://school.koreacharts.com/school/meals/B000012565/contents.html"

    match = re.search(r'(\d{1,2})[./](\d{1,2})', user_msg)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        try:
            date = datetime(datetime.today().year, month, day)
            return jsonify({'reply': get_school_meal(school_url, day=day)})
        except:
            return jsonify({'reply': "❗ 올바른 날짜 형식이 아니에요."})

    if "오늘" in user_msg:
        reply = get_school_meal(school_url, day=get_day_offset(0))
    elif "내일 모레" in user_msg:
        reply = get_school_meal(school_url, day=get_day_offset(2))
    elif "내일" in user_msg:
        reply = get_school_meal(school_url, day=get_day_offset(1))
    elif "월요일" in user_msg:
        ty = 0
        reply = get_school_meal(school_url, day=get_day_offset(yoil_count(ty)))
    elif "화요일" in user_msg:
        ty = 1
        reply = get_school_meal(school_url, day=get_day_offset(yoil_count(ty)))
    elif "수요일" in user_msg:
        ty = 2
        reply = get_school_meal(school_url, day=get_day_offset(yoil_count(ty)))
    elif "목요일" in user_msg:
        ty = 3
        reply = get_school_meal(school_url, day=get_day_offset(yoil_count(ty)))
    elif "금요일" in user_msg:
        ty = 4
        reply = get_school_meal(school_url, day=get_day_offset(yoil_count(ty)))
    elif "토요일" in user_msg:
        reply = "토요일엔 학교를 안 갑니다"
    elif "일요일" in user_msg:
        reply = "일요일엔 학교를 안 갑니다"
    else:
        reply = "🤖 '오늘 급식 알려줘', '내일 급식 알려줘'처럼 말씀해보세요!"

    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
