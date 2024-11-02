from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from generate1 import analyze_content  # 從 generate1.py 導入分析函數

app = Flask(__name__)

def fetch_ptt_articles(board, keyword):
    url = f'https://www.ptt.cc/bbs/{board}/search'
    response = requests.get(url, params={'q': keyword})
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for entry in soup.find_all('div', class_='r-ent'):
        title_elem = entry.find('div', class_='title')
        if title_elem and title_elem.a:
            title = title_elem.a.text
            link = title_elem.a['href']
            full_link = f'https://www.ptt.cc{link}'
            article_response = requests.get(full_link)
            article_soup = BeautifulSoup(article_response.text, 'html.parser')

            # 提取文章內容，僅保留 richcontent 前的部分，並去除 HTML 標籤
            content_elem = article_soup.find('div', id='main-content')
            content = ""
            if content_elem:
                for elem in content_elem.children:
                    if elem.name == "div" and "richcontent" in elem.get("class", []):
                        break
                    content += str(elem)
            
            # 去除 HTML 標籤，只保留純文本
            content_text = BeautifulSoup(content, 'html.parser').get_text()

            # 使用 Gemini 分析去除 HTML 標籤的純文本內容
            # analysis = analyze_content(content_text)

            # 提取回覆
            replies = []
            for push in article_soup.find_all('div', class_='push'):
                user = push.find('span', class_='push-userid')
                reply_content = push.find('span', class_='push-content')
                if user and reply_content:
                    reply_text = f"{user.text.strip()} {reply_content.text.strip()}"
                    replies.append(reply_text)  # 保留回覆者名稱和回覆內容
            
            analysis = analyze_content(replies)
            # results.append({'title': title, 'content': content_text, 'analysis': analysis, 'replies': replies})
            results.append({'title': title, 'content': content_text, 'analysis': analysis, 'replies': replies})
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        board = request.form['board']  # 從表單獲取看板
        keyword = request.form['keyword']  # 從表單獲取關鍵字
        results = fetch_ptt_articles(board, keyword)  # 爬取相關文章並進行分析
    return render_template('index1.html', results=results)  # 返回結果至模板

if __name__ == '__main__':
    app.run(debug=True)
