from flask import Flask, request, make_response, send_from_directory, redirect
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__, static_folder='static')

TARGET_DOMAIN = "https://jwxt.sztu.edu.cn"
TRANSLATE_SCRIPT_PATH = "/static/translation.js"
ENGLISH_URL_PREFIX = "/en"

@app.route('/')
def index():
    # 按实际首页路径修改（如有需要）
    return redirect(f"{ENGLISH_URL_PREFIX}/jsxsd/framework/jsMain.htmlx")

@app.route(f"{ENGLISH_URL_PREFIX}/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_en(path):
    return proxy_request(path, inject_script=True)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

def proxy_request(path, inject_script):
    target_url = f"{TARGET_DOMAIN}/{path}"
    proxied_response = forward_request(target_url)
    if not proxied_response:
        return "代理请求失败", 502

    content_type = proxied_response.headers.get("Content-Type", "")
    response_data = proxied_response.content

    if inject_script and "text/html" in content_type:
        html = response_data.decode(proxied_response.encoding or "utf-8", errors="ignore")
        modified_html = inject_translate_script(html)
        modified_html = fix_relative_urls(modified_html)
        response_data = modified_html.encode("utf-8")

    response = make_response(response_data)
    for key, value in proxied_response.headers.items():
        # 排除Content-Length、Content-Encoding、Transfer-Encoding
        if key.lower() not in ["content-length", "content-encoding", "transfer-encoding"]:
            response.headers[key] = value
    return response

def forward_request(target_url):
    try:
        headers = dict(request.headers)
        headers.pop("Host", None)
        params = request.args.to_dict(flat=False)
        # 修正文件上传
        files = {}
        for k, v in request.files.items():
            files[k] = (v.filename, v.stream, v.mimetype)
        if request.method == "GET":
            response = requests.get(target_url, headers=headers, cookies=request.cookies, params=params, allow_redirects=False)
        elif request.method == "POST":
            response = requests.post(target_url, headers=headers, cookies=request.cookies, data=request.form, files=files if files else None, allow_redirects=False)
        else:
            response = requests.request(method=request.method, url=target_url, headers=headers, cookies=request.cookies, data=request.data, allow_redirects=False)
        return response
    except Exception as e:
        app.logger.error(f"请求转发失败: {str(e)}")
        return None

def inject_translate_script(html):
    try:
        soup = BeautifulSoup(html, "html.parser")
        body_tag = soup.find("body")
        if body_tag:
            script_tag = soup.new_tag("script", src=TRANSLATE_SCRIPT_PATH)
            if hasattr(body_tag, 'insert'):
                body_tag.insert(len(body_tag.contents), script_tag)
            else:
                body_tag.append(script_tag)
            return str(soup)
        else:
            return html
    except Exception as e:
        app.logger.error(f"HTML解析失败: {str(e)}")
        return html

def fix_relative_urls(html):
    # 只修复非/static/的绝对路径
    html = re.sub(
        r'(href|src|action)="(/)(?!/|static/)',  # 不以//或/static/开头
        rf'\1="{ENGLISH_URL_PREFIX}/\2',
        html
    )
    # 修复相对路径（不以/或http开头）：css/style.css → /en/css/style.css
    html = re.sub(
        r'(href|src|action)="((?!/|http|https|static/).+?)"',
        rf'\1="{ENGLISH_URL_PREFIX}/\2"',
        html
    )
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)