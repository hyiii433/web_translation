from flask import Flask, request, make_response, send_from_directory, redirect
import requests
from bs4 import BeautifulSoup
import re
import urllib3

# 关闭 SSL 证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, static_folder='static')

TARGET_DOMAIN = "https://jwxt.sztu.edu.cn"
TRANSLATE_SCRIPT_PATH = "/static/translation.js"
ENGLISH_URL_PREFIX = "/en"

# 在文件顶部定义你的cookie
MY_COOKIE = 'JSESSIONID=BFF5E4D6F5041A05F3E7355AFE9F5AF4; SERVERID=121'
MY_COOKIE_DICT = {item.split('=')[0]: item.split('=')[1] for item in MY_COOKIE.split('; ')}

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
    app.logger.info(f"代理请求: {path} -> {target_url}")
    
    proxied_response = forward_request(target_url)
    if not proxied_response:
        app.logger.error(f"代理请求失败: {path}")
        return "代理请求失败", 502

    content_type = proxied_response.headers.get("Content-Type", "")
    response_data = proxied_response.content
    
    app.logger.info(f"响应状态: {proxied_response.status_code}, 内容类型: {content_type}")

    if inject_script and "text/html" in content_type:
        html = response_data.decode(proxied_response.encoding or "utf-8", errors="ignore")
        
        modified_html = inject_translate_script(html)
        modified_html = fix_relative_urls(modified_html)
        
        response_data = modified_html.encode("utf-8")
        app.logger.info(f"已注入翻译脚本: {path}")

    response = make_response(response_data)
    for key, value in proxied_response.headers.items():
        # 排除Content-Length、Content-Encoding、Transfer-Encoding
        if key.lower() not in ["content-length", "content-encoding", "transfer-encoding"]:
            response.headers[key] = value
    return response

def fix_relative_urls(html):
    import re
    
    # 调试：输出原始HTML中的iframe信息
    if "iframe" in html.lower():
        iframe_matches = re.findall(r'<iframe[^>]*src=["\']([^"\']*)["\'][^>]*>', html, re.IGNORECASE)
        jsxsd_iframes = [iframe for iframe in iframe_matches if iframe and iframe.startswith('/jsxsd/')]
        if jsxsd_iframes:
            app.logger.info(f"需要修复的iframe: {jsxsd_iframes}")
    
    # 调试：显示原始HTML中的iframe标签
    if "iframe" in html.lower():
        iframe_tags = re.findall(r'<iframe[^>]*>', html, re.IGNORECASE)
        for tag in iframe_tags:
            if 'src=' in tag and '/jsxsd/' in tag:
                app.logger.info(f"原始iframe标签: {tag}")
    
    # 修复iframe的src属性 - 更精确的匹配
    original_html = html
    html = re.sub(
        r'(src=)["\'](/jsxsd/[^"\']*)["\']',
        rf'\1"{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 调试：检查是否发生了替换
    if html != original_html:
        app.logger.info("iframe src替换已执行")
    else:
        app.logger.info("iframe src替换未执行，尝试备用方法")
        # 备用方法：直接字符串替换
        html = html.replace('src="/jsxsd/', f'src="{ENGLISH_URL_PREFIX}/jsxsd/')
        html = html.replace("src='/jsxsd/", f"src='{ENGLISH_URL_PREFIX}/jsxsd/")
    
    # 修复form的action属性 - 匹配所有/jsxsd/开头的路径
    html = re.sub(
        r'(<form[^>]*action=)["\'](/jsxsd/[^"\']*)["\']',
        rf'\1"{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 修复链接的href属性 - 匹配所有/jsxsd/开头的路径
    html = re.sub(
        r'(<a[^>]*href=)["\'](/jsxsd/[^"\']*)["\']',
        rf'\1"{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 修复图片的src属性 - 匹配所有/jsxsd/开头的路径
    html = re.sub(
        r'(<img[^>]*src=)["\'](/jsxsd/[^"\']*)["\']',
        rf'\1"{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 修复script的src属性 - 匹配所有/jsxsd/开头的路径
    html = re.sub(
        r'(<script[^>]*src=)["\'](/jsxsd/[^"\']*)["\']',
        rf'\1"{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 修复link的href属性 - 匹配所有/jsxsd/开头的路径
    html = re.sub(
        r'(<link[^>]*href=)["\'](/jsxsd/[^"\']*)["\']',
        rf'\1"{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 修复JavaScript中的路径 - 匹配所有/jsxsd/开头的路径（包括有扩展名和没有扩展名的）
    html = re.sub(
        r'(["\'])(/jsxsd/[^"\']*)(["\'])',
        rf'\1{ENGLISH_URL_PREFIX}\2\3',
        html
    )
    
    # 调试：检查修复后的iframe
    if "iframe" in html.lower():
        iframe_matches_after = re.findall(r'<iframe[^>]*src=["\']([^"\']*)["\'][^>]*>', html, re.IGNORECASE)
        jsxsd_iframes_after = [iframe for iframe in iframe_matches_after if iframe and iframe.startswith('/en/jsxsd/')]
        if jsxsd_iframes_after:
            app.logger.info(f"修复后的iframe: {jsxsd_iframes_after}")
        
        # 显示修复后的iframe标签
        iframe_tags_after = re.findall(r'<iframe[^>]*>', html, re.IGNORECASE)
        for tag in iframe_tags_after:
            if 'src=' in tag and '/en/jsxsd/' in tag:
                app.logger.info(f"修复后iframe标签: {tag}")
    
    return html

def forward_request(target_url):
    try:
        headers = dict(request.headers)
        headers.pop("Host", None)
        params = request.args.to_dict(flat=False)
        files = {}
        for k, v in request.files.items():
            files[k] = (v.filename, v.stream, v.mimetype)
        # 合并用户请求的cookie和你的cookie
        cookies = request.cookies.copy()
        cookies.update(MY_COOKIE_DICT)
        
        # 添加超时设置
        timeout = 30
        
        if request.method == "GET":
            response = requests.get(target_url, headers=headers, cookies=cookies, params=params, allow_redirects=False, verify=False, timeout=timeout)
        elif request.method == "POST":
            response = requests.post(target_url, headers=headers, cookies=cookies, data=request.form, files=files if files else None, allow_redirects=False, verify=False, timeout=timeout)
        else:
            response = requests.request(method=request.method, url=target_url, headers=headers, cookies=cookies, data=request.data, allow_redirects=False, verify=False, timeout=timeout)
        return response
    except requests.exceptions.Timeout:
        app.logger.error(f"请求超时: {target_url}")
        return None
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)