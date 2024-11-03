from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import asyncio
import time
from generate1 import analyze_content  # 從 generate1.py 導入分析函數

app = Flask(__name__)

async def fetch_article_content(link):
    """獲取單篇文章內容和回覆"""
    full_link = f'https://www.ptt.cc{link}'
    article_response = requests.get(full_link)
    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    
    # 提取文章內容
    content_elem = article_soup.find('div', id='main-content')
    content = ""
    if content_elem:
        for elem in content_elem.children:
            if elem.name == "div" and "richcontent" in elem.get("class", []):
                break
            content += str(elem)
    
    content_text = BeautifulSoup(content, 'html.parser').get_text()  # 去除 HTML 標籤
    
    # 提取回覆
    replies = []
    for push in article_soup.find_all('div', class_='push'):
        user = push.find('span', class_='push-userid')
        reply_content = push.find('span', class_='push-content')
        if user and reply_content:
            reply_text = f"{user.text.strip()} {reply_content.text.strip()}"
            replies.append(reply_text)
    
    return content_text, replies, full_link  # 返回文章內容、回覆和原始連結

async def fetch_ptt_articles(board, keyword, prompt):
    url = f'https://www.ptt.cc/bbs/{board}/search'
    response = requests.get(url, params={'q': keyword})
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    # 初始化 content_all 變數，用於存儲所有內文與回覆
    content_all = ""

    # 限制文章數以減少 API 調用
    article_links = []
    for entry in soup.find_all('div', class_='r-ent')[:5]:  # 僅處理前 5 篇文章
        title_elem = entry.find('div', class_='title')
        if title_elem and title_elem.a:
            title = title_elem.a.text
            link = title_elem.a['href']
            article_links.append((title, link))

    for title, link in article_links:
        content_text, replies, full_link = await fetch_article_content(link)  # 獲取原始連結

        # 將內文和回覆串接到 content_all 中
        content_all += f"標題: {title}\n"
        content_all += f"內容: {content_text}\n"
        content_all += "回覆:\n" + "\n".join(replies) + "\n\n"
        
        # 批量處理並限制 API 調用頻率
        try:
            analysis = analyze_content(replies, prompt=prompt)  # 批量分析回覆
            results.append({
                'title': title,
                'content': content_text,
                'analysis': analysis,
                'replies': replies,
                'url': full_link  # 加入原始文章連結
            })
            time.sleep(1)  # 避免 API 請求過於頻繁
        except Exception as e:
            print(f"API 調用失敗：{e}")
            continue  # 如果發生錯誤，跳過該文章

    # 對 content_all 執行分析
    overall_analysis = analyze_content(content_all, prompt=prompt)

    # 返回 results 和 content_all 分析結果
    return results, overall_analysis

@app.route('/', methods=['GET', 'POST'])
async def index():
    results = []
    overall_analysis = ""
    if request.method == 'POST':
        board = request.form['board']
        keyword = request.form['keyword']
        prompt = request.form['prompt']
        results, overall_analysis = await fetch_ptt_articles(board, keyword, prompt=prompt)
    return render_template('index1.html', results=results, overall_analysis=overall_analysis)


if __name__ == '__main__':
    app.run(port=5050)
