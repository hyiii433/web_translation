from flask import Flask, request, make_response, send_from_directory, redirect
import requests
from bs4 import BeautifulSoup
import re
import urllib3
import time
import threading
from datetime import datetime, timedelta

# 关闭 SSL 证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, static_folder='static')

TARGET_DOMAIN = "https://jwxt.sztu.edu.cn"
TRANSLATE_SCRIPT_PATH = "/static/translation.js"
ENGLISH_URL_PREFIX = "/en"

# 登录配置
LOGIN_URL = "https://auth.sztu.edu.cn/idp/authcenter/ActionAuthChain?entityId=jiaowu"
USERNAME = "20210960"
PASSWORD = "i2A4$0*B"

# Cookie管理
class CookieManager:
    def __init__(self):
        self.cookies = {}
        self.last_update = None
        self.session = requests.Session()
        self.session.verify = False
        self.lock = threading.Lock()
        
    def login(self):
        """自动登录获取cookie"""
        try:
            app.logger.info("开始自动登录...")
            
            # 第一步：访问登录页面获取初始cookie和表单数据
            response = self.session.get(LOGIN_URL, timeout=30)
            if response.status_code != 200:
                app.logger.error(f"访问登录页面失败: {response.status_code}")
                return False
            
            # 解析登录页面，获取表单字段
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找登录表单
            login_form = soup.find('form')
            if not login_form:
                app.logger.error("未找到登录表单")
                return False
            
            # 获取表单action
            form_action = login_form.get('action', LOGIN_URL)
            if form_action.startswith('/'):
                form_action = 'https://auth.sztu.edu.cn' + form_action
            
            # 获取所有隐藏字段
            hidden_inputs = login_form.find_all('input', type='hidden')
            login_data = {}
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value', '')
                if name:
                    login_data[name] = value
            
            # 添加用户名和密码
            login_data['username'] = USERNAME
            login_data['password'] = PASSWORD
            
            # 设置登录请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': LOGIN_URL,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            app.logger.info(f"提交登录表单到: {form_action}")
            app.logger.info(f"登录数据: {login_data}")
            
            # 提交登录表单
            response = self.session.post(form_action, data=login_data, headers=headers, timeout=30, allow_redirects=True)
            
            app.logger.info(f"登录响应状态: {response.status_code}")
            app.logger.info(f"登录后URL: {response.url}")
            
            # 检查登录是否成功
            if response.status_code == 200:
                # 检查是否重定向到教务系统
                if 'jwxt.sztu.edu.cn' in response.url or 'sztu.edu.cn' in response.url:
                    app.logger.info("登录成功！")
                    self.cookies = dict(self.session.cookies)
                    self.last_update = datetime.now()
                    app.logger.info(f"获取到的cookies: {self.cookies}")
                    return True
                else:
                    # 检查响应内容是否包含登录成功的关键词
                    content = response.text.lower()
                    if 'login' in content or 'auth' in content or '登录' in content:
                        app.logger.error("登录失败，仍在登录页面")
                        return False
                    else:
                        app.logger.info("登录可能成功，继续检查...")
                        self.cookies = dict(self.session.cookies)
                        self.last_update = datetime.now()
                        app.logger.info(f"获取到的cookies: {self.cookies}")
                        return True
            else:
                app.logger.error(f"登录失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            app.logger.error(f"登录过程中发生错误: {str(e)}")
            return False
    
    def get_cookies(self):
        """获取当前有效的cookies"""
        with self.lock:
            # 如果cookies为空或超过30分钟，重新登录
            if not self.cookies or (self.last_update and datetime.now() - self.last_update > timedelta(minutes=30)):
                if self.login():
                    return self.cookies.copy()
                else:
                    return {}
            return self.cookies.copy()
    
    def update_cookies(self, new_cookies):
        """更新cookies（从教务系统响应中获取）"""
        with self.lock:
            self.cookies.update(new_cookies)
            self.last_update = datetime.now()

# 创建全局cookie管理器
cookie_manager = CookieManager()

# 初始化时尝试登录
def init_login():
    """初始化时尝试登录"""
    try:
        if cookie_manager.login():
            app.logger.info("初始登录成功")
        else:
            app.logger.warning("初始登录失败，将使用空cookie")
    except Exception as e:
        app.logger.error(f"初始化登录失败: {str(e)}")

# 启动时执行登录
init_login()

@app.route('/')
def index():
    return redirect(f"{ENGLISH_URL_PREFIX}/jsxsd/framework/jsMain.htmlx")

@app.route(f"{ENGLISH_URL_PREFIX}/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_en(path):
    return proxy_request(path, inject_script=True)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/refresh-cookie")
def refresh_cookie():
    """手动刷新cookie"""
    try:
        if cookie_manager.login():
            return {"status": "success", "message": "Cookie刷新成功", "cookies": cookie_manager.get_cookies()}
        else:
            return {"status": "error", "message": "Cookie刷新失败"}, 500
    except Exception as e:
        return {"status": "error", "message": f"刷新失败: {str(e)}"}, 500

@app.route("/cookie-status")
def cookie_status():
    """查看cookie状态"""
    cookies = cookie_manager.get_cookies()
    last_update = cookie_manager.last_update
    return {
        "cookies": cookies,
        "last_update": last_update.isoformat() if last_update else None,
        "cookie_count": len(cookies)
    }

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
        
        # 调试：输出iframe信息
        if "iframe" in html.lower():
            import re
            iframes = re.findall(r'<iframe[^>]*src="([^"]*)"[^>]*>', html, re.IGNORECASE)
            app.logger.info(f"发现iframe: {iframes}")
        
        modified_html = inject_translate_script(html)
        modified_html = fix_relative_urls(modified_html)
        response_data = modified_html.encode("utf-8")
        app.logger.info(f"已注入翻译脚本: {path}")

    response = make_response(response_data)
    for key, value in proxied_response.headers.items():
        if key.lower() not in ["content-length", "content-encoding", "transfer-encoding"]:
            response.headers[key] = value
    return response

def fix_relative_urls(html):
    # 1. 修复HTML标签中的绝对路径（以/开头，排除//和/static/）
    html = re.sub(
        r'(href|src|action)="(/)(?!/|static/)',  # 不以//或/static/开头
        rf'\1="{ENGLISH_URL_PREFIX}\2',  # 移除多余的斜杠
        html
    )
    
    # 2. 修复相对路径（不以/或http开头）
    html = re.sub(
        r'(href|src|action)="((?!/|http|https|static/).+?)"',
        rf'\1="{ENGLISH_URL_PREFIX}/\2"',
        html
    )
    
    # 3. 修复JavaScript字符串中的路径
    # 匹配JavaScript中的字符串，如 'jsxsd/xxx' 或 "/jsxsd/xxx"
    html = re.sub(
        r'(["\'])(/jsxsd/[^"\']*)(["\'])',
        rf'\1{ENGLISH_URL_PREFIX}\2\3',
        html
    )
    
    # 4. 修复JavaScript中的window.open、location.href等
    html = re.sub(
        r'(window\.open|location\.href|location\.replace)\s*\(\s*(["\'])(/jsxsd/[^"\']*)\2',
        rf'\1(\2{ENGLISH_URL_PREFIX}\3\2',
        html
    )
    
    # 5. 修复JavaScript中的变量赋值，如 var url = '/jsxsd/xxx'
    html = re.sub(
        r'(\w+\s*=\s*["\'])(/jsxsd/[^"\']*)(["\'])',
        rf'\1{ENGLISH_URL_PREFIX}\2\3',
        html
    )
    
    # 6. 修复iframe的src属性（更全面的匹配）
    html = re.sub(
        r'(src)="(/jsxsd/[^"]*)"',
        rf'\1="{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 7. 修复form的action属性
    html = re.sub(
        r'(action)="(/jsxsd/[^"]*)"',
        rf'\1="{ENGLISH_URL_PREFIX}\2"',
        html
    )
    
    # 8. 修复CSS中的url()路径
    html = re.sub(
        r'(url\s*\(\s*["\']?)(/jsxsd/[^"\')\s]*)(["\']?\s*\))',
        rf'\1{ENGLISH_URL_PREFIX}\2\3',
        html
    )
    
    # 9. 修复AJAX请求中的URL
    html = re.sub(
        r'(\$\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\'])(/jsxsd/[^"\']*)(["\'])',
        rf'\1{ENGLISH_URL_PREFIX}\2\3',
        html
    )
    
    # 10. 修复其他可能的路径引用
    html = re.sub(
        r'(["\'])(/jsxsd/[^"\']*)(["\'])',
        rf'\1{ENGLISH_URL_PREFIX}\2\3',
        html
    )
    
    return html

def forward_request(target_url):
    try:
        headers = dict(request.headers)
        headers.pop("Host", None)
        params = request.args.to_dict(flat=False)
        files = {}
        for k, v in request.files.items():
            files[k] = (v.filename, v.stream, v.mimetype)
        
        # 获取当前有效的cookies
        cookies = request.cookies.copy()
        auto_cookies = cookie_manager.get_cookies()
        cookies.update(auto_cookies)
        
        # 添加超时设置
        timeout = 30
        
        if request.method == "GET":
            response = requests.get(target_url, headers=headers, cookies=cookies, params=params, allow_redirects=False, verify=False, timeout=timeout)
        elif request.method == "POST":
            response = requests.post(target_url, headers=headers, cookies=cookies, data=request.form, files=files if files else None, allow_redirects=False, verify=False, timeout=timeout)
        else:
            response = requests.request(method=request.method, url=target_url, headers=headers, cookies=cookies, data=request.data, allow_redirects=False, verify=False, timeout=timeout)
        
        # 如果请求成功，更新cookies
        if response.status_code == 200:
            cookie_manager.update_cookies(dict(response.cookies))
        
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