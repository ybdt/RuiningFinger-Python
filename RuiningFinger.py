#!/usr/bin/env python3
# author: ybdt


"""
指纹识别参考项目：
https://github.com/Funsiooo/chunsou
https://github.com/EASY233/Finger

坑1：requests中timeout设置为5，目标 https://www.kanwz.net 会报超时异常，将timeout改为10，不再报错
坑2：目标 https://4976.xiajindairy.cn:8443 会报错 SSLV3_ALERT_ILLEGAL_PARAMETER，需要做异常处理
"""


import json
import random
import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import mmh3
import base64
import warnings
from urllib3.exceptions import InsecureRequestWarning
import argparse
from colorama import Fore, Style
import chardet
import queue
import threading
import time
import pandas as pd
import os
import urllib.request


# 屏蔽提醒
warnings.filterwarnings('ignore', category=InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning, message="Caught 'unbalanced parenthesis at position 119'")


# 定义全局变量
counter = 0
_3xx_url = ""


# 创建一个锁，以便线程能够安全地访问计数器
# counter_lock = threading.Lock()


def get_icon_hash(content):
    def mmh3_hash32(raw_bytes, is_uint32=True):
        h32 = mmh3.hash(raw_bytes)
        if is_uint32:
            return str(h32 & 0xffffffff)
        else:
            return str(h32)

    def stand_base64(braw) -> bytes:
        bckd = base64.standard_b64encode(braw)
        buffer = bytearray()
        for i, ch in enumerate(bckd):
            buffer.append(ch)
            if (i + 1) % 76 == 0:
                buffer.append(ord('\n'))
        buffer.append(ord('\n'))
        return bytes(buffer)

    return mmh3_hash32(stand_base64(content))


def get_icon_url(html, url):
    icon_index = html.find("<link rel=\"icon\"")
    shortcut_index = html.find("<link rel=\"shortcut icon\"")
    if (icon_index == -1) or (shortcut_index == -1):
        favicon_url = urljoin(url, "/favicon.ico")
        return favicon_url
    else:
        if icon_index != -1:
            end_index = html.find(">", icon_index)
            link_tag = html[icon_index:end_index]
            favicon_path = link_tag.split('href="')[1].split('"')[0]
        elif shortcut_index != -1:
            end_index = html.find(">", shortcut_index)
            link_tag = html[shortcut_index:end_index]
            favicon_path = link_tag.split('href="')[1].split('"')[0]
        favicon_url = urljoin(url, favicon_path)
        return favicon_url


def get_headers():
    user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 YaBrowser/21.6.0.615 Yowser/2.5 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Edge/91.0.864.59',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Linux; Android 11; SM-G991U Build/RP1A.200720.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.6 Safari/532.0',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1 ; x64; en-US; rv:1.9.1b2pre) Gecko/20081026 Firefox/3.1b2pre',
        'Opera/10.60 (Windows NT 5.1; U; zh-cn) Presto/2.6.30 Version/10.60',
        'Opera/8.01 (J2ME/MIDP; Opera Mini/2.0.4062; en; U; ssr)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; ; rv:1.9.0.14) Gecko/2009082707 Firefox/3.0.14',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4 ( .NET CLR 3.5.30729)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16',
        'Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 '
        'Safari/533.18.5',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5660.225 Safari/537.36'
    ]
    random_user_agent = random.choice(user_agent)
    headers = {
        'Accept': 'application/x-shockwave-flash, image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, '
                  'application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*',
        'User-agent': random_user_agent,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Connection': 'close'
    }
    return headers


def print_redirect_finger(counter, url, status_code_str, redirect_url, redirect_status_code_str, title_str, cms):
    print(str(counter) + " " +
          Fore.RED + url + Style.RESET_ALL + "  |  " +
          Fore.YELLOW + status_code_str + Style.RESET_ALL + "  |  " +
          Fore.RED + redirect_url + Style.RESET_ALL + "  |  " +
          Fore.YELLOW + redirect_status_code_str + Style.RESET_ALL + "  |  " +
          Fore.BLUE + title_str + Style.RESET_ALL + "  |  " +
          Fore.GREEN + cms + Style.RESET_ALL + "  |"
    )


def print_finger(counter, url, status_code_str, title_str, cms):
    print(str(counter) + " " +
          Fore.RED + url + Style.RESET_ALL + "  |  " +
          Fore.YELLOW + status_code_str + Style.RESET_ALL + "  |  " +
          Fore.BLUE + title_str + Style.RESET_ALL + "  |  " +
          Fore.GREEN + cms + Style.RESET_ALL + "  |"
    )


def _5xx_redirect_print(counter, url, status_code, redirect_url, redirect_status_code):
    if redirect_status_code == 500:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Internal Server Error", "", "")
    elif redirect_status_code == 501:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Method Not Implemented", "", "")
    elif redirect_status_code == 502:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Bad Gateway", "", "")
    elif redirect_status_code == 503:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Service Unavailable", "", "")
    elif redirect_status_code == 530:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " 非官方，Cloudflare使用", "", "")
    else:
        print("_5xx_redirect_print error")


def _5xx_print(counter, url, status_code):
    if status_code == 500:
        print_finger(counter, url, str(status_code) + " Internal Server Error", "", "")
    elif status_code == 501:
        print_finger(counter, url, str(status_code) + " Method Not Implemented", "", "")
    elif status_code == 502:
        print_finger(counter, url, str(status_code) + " Bad Gateway", "", "")
    elif status_code == 503:
        print_finger(counter, url, str(status_code) + " Service Unavailable", "", "")
    elif status_code == 530:
        print_finger(counter, url, str(status_code) + " 非官方，Cloudflare使用", "", "")


def _4xx_redirect_print(counter, url, status_code, redirect_url, redirect_status_code):
    if redirect_status_code == 400:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Bad Request", "", "")
    elif redirect_status_code == 405:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Method Not Allowed", "", "")
    elif redirect_status_code == 412:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Precondition Failed", "", "")
    elif redirect_status_code == 415:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Unsupported Media Type", "", "")
    elif redirect_status_code == 426:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " 服务器拒绝请求，直到客户端使用更新的协议", "", "")
    elif redirect_status_code == 444:
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code) + " Nginx关闭连接且未向客户端发送响应", "", "")
    else:
        print("_4xx_redirect_print error")


def _4xx_print(counter, url, status_code):
    if status_code == 400:
        print_finger(counter, url, str(status_code) + " Bad Request", "", "")
    elif status_code == 405:
        print_finger(counter, url, str(status_code) + " Method Not Allowed", "", "")
    elif status_code == 412:
        print_finger(counter, url, str(status_code) + " Precondition Failed", "", "")
    elif status_code == 415:
        print_finger(counter, url, str(status_code) + " Unsupported Media Type", "", "")
    elif status_code == 426:
        print_finger(counter, url, str(status_code) + " 服务器拒绝请求，直到客户端使用更新的协议", "", "")
    elif status_code == 444:
        print_finger(counter, url, str(status_code) + " Nginx关闭连接且未向客户端发送响应", "", "")


def finger_redirect_identify_core(counter, response, url, status_code, redirect_url, redirect_status_code, fa1, fa2, fa3, fingers, csv_url_list, csv_status_code_list, csv_title_list, csv_cms_list):
    headers_str = str(response.headers)

    content = response.content
    encoding = chardet.detect(content)['encoding']
    if encoding is not None:  # 可从html中提取到encoding
        try:
            try:
                html_body = content.decode(encoding)
            except UnicodeDecodeError:
                html_body = content.decode("gb18030")
        except Exception as e:
            print(f"{counter} not write to file, for debug 7 ---- 目标 {url} 使用字符集 {encoding}、gb18030 解码时报错 {e}")
            return
    else:  # 不能从html中提取到encoding
        try:
            try:
                html_body = content.decode(encoding)
            except UnicodeDecodeError:
                html_body = content.decode("gb18030")
        except Exception as e:
            print(f"{counter} not write to file, for debug 8 ---- 目标 {url} 使用字符集 {encoding}、gb18030 解码时报错 {e}")
            return

    if html_body is not None:
        soup = BeautifulSoup(html_body, "html.parser")
        # soup = BeautifulSoup(urllib.request.urlopen(redirect_url), "html.parser")
        title = soup.title
        if title is None:
            title_str = ""
        elif title.string is None:
            title_str = ""
        elif title.string == "":
            title_str = ""
        else:
            title_str = title.string.strip()

        # 获取icon hash
        icon_url = get_icon_url(html_body, url)
        http_request_return_str = http_request(counter, icon_url, fa1, fa2, fa3)
        if http_request_return_str == "continue":
            return
        else:
            icon_response = http_request_return_str
        icon_content = icon_response.content
        icon_hash = get_icon_hash(icon_content)

        # 从指纹库中匹配指纹
        for finger in fingers:
            method = finger["method"]
            location = finger["location"]
            keyword_list = finger["keyword"]
            cms = finger["cms"]
            if (method == "keyword") and (location == "title"):
                if (title is not None) and (title != ""):  # 如果title不为None且不为空，基于title判断指纹
                    if keyword_list[0] in title:  # 编写小工具，检测后发现，title中的关键字只有一个，不需要迭代
                        csv_url_list.append(url)
                        csv_status_code_list.append(status_code)
                        csv_title_list.append(title_str)
                        csv_cms_list.append(cms)
                        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code), title_str, cms)
                        return  # 跳出指纹识别
                    else:
                        continue  # 跳到下一个指纹
                else:
                    csv_url_list.append(url)
                    csv_status_code_list.append(status_code)
                    csv_title_list.append("")
                    csv_cms_list.append("")
                    print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code), "", "")
                    return  # 跳出指纹识别
            elif (method == "keyword") and (location == "header"):
                for keyword in keyword_list:
                    if keyword in headers_str:
                        csv_url_list.append(url)
                        csv_status_code_list.append(status_code)
                        csv_title_list.append(title_str)
                        csv_cms_list.append(cms)
                        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code), title_str, cms)
                        return  # 跳出指纹识别
                    else:
                        continue  # 跳到当前指纹关键字列表中的下一个
                continue  # 跳到下一个指纹
            elif (method == "keyword") and (location == "body"):
                if all(keyword in html_body for keyword in keyword_list):
                    csv_url_list.append(url)
                    csv_status_code_list.append(status_code)
                    csv_title_list.append(title_str)
                    csv_cms_list.append(cms)
                    print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code), title_str, cms)
                    return  # 跳出指纹识别
                else:
                    continue  # 跳到下一个指纹
            elif (method == "icon_hash") and (location == "body"):
                if keyword_list == icon_hash:  # icon_hash的关键字只有一个，不需要迭代
                    csv_url_list.append(url)
                    csv_status_code_list.append(status_code)
                    csv_title_list.append(title_str)
                    csv_cms_list.append(cms)
                    print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code), title_str, cms)
                    return  # 跳出指纹识别
                else:
                    continue  # 进入下一个指纹
        csv_url_list.append(url)
        csv_status_code_list.append(status_code)
        csv_title_list.append("")
        csv_cms_list.append("")
        print_redirect_finger(counter, url, str(status_code), redirect_url, str(redirect_status_code), "", "")

    else:
        print(f"{counter} 目标 {url} html_body 为 None")


def _3xx_http_request(counter, url, fa1, fa2, fa3):
    headers = get_headers()
    try:
        response = requests.get(url=url, headers=headers, timeout=10, verify=False, allow_redirects=True)
    except requests.exceptions.SSLError:
        print(f"{counter} not write to file, for debug 4 ---- 跟目标 {url} 建立SSL连接时报错")
        return "continue"
    except requests.exceptions.ConnectTimeout:
        print(f"{counter} 跟目标 {url} 建立连接超时")
        fa1.write("跟目标 {} 建立连接超时".format(url) + "\n")
        return "continue"
    except requests.exceptions.ReadTimeout:
        print(f"{counter} 跟目标 {url} 建立连接后读取数据超时")
        fa2.write("跟目标 {} 建立连接后读取数据超时".format(url) + "\n")
        return "continue"
    except requests.exceptions.ConnectionError:
        print(f"{counter} 跟目标 {url} 建立连接时 连接被重置 或 连接被拒绝 或 网络不可达")
        fa3.write("跟目标 {} 建立连接时 连接被重置 或 连接被拒绝 或 网络不可达".format(url) + "\n")
        return "continue"
    except Exception as e:
        print(f"{counter} not write to file, for debug 5 ---- 目标 {url} 报错 {e}")
        return "continue"
    return response


def _3xx_get_redirect_url(response, url):
    location_str = response.headers["Location"]
    if location_str.startswith("http://") or location_str.startswith("https://"):
        redirect_url = response.headers["Location"]
    else:
        if response.headers["Location"].startswith("./"):
            web_path = response.headers["Location"][2:]
        elif response.headers["Location"].startswith("/"):
            web_path = response.headers["Location"][1:]
        else:
            web_path = response.headers["Location"]
        if not url.endswith == "/":
            url = url + "/"
        redirect_url = url + web_path
    return redirect_url


def finger_identify_core(counter, response, url, status_code, fa1, fa2, fa3, fingers, csv_url_list, csv_status_code_list, csv_title_list, csv_cms_list):
    headers_str = str(response.headers)

    content = response.content
    encoding = chardet.detect(content)['encoding']
    if encoding is not None:  # 可从html中提取到encoding
        try:
            try:
                html_body = content.decode(encoding)
            except UnicodeDecodeError:
                html_body = content.decode("gb18030")
        except Exception as e:
            print(f"{counter} not write to file, for debug 3 ---- 目标 {url} 使用字符集 {encoding}、gb18030 解码时报错 {e}")
            return
    else:  # 不能从html中提取到encoding
        try:
            try:
                html_body = content.decode("utf-8")
            except UnicodeDecodeError:
                html_body = content.decode("gb18030")
        except Exception as e:
            print(f"{counter} not write to file, for debug 4 ---- 目标 {url} 使用字符集 utf-8、gb18030 解码时报错 {e}")
            return

    if html_body is not None:
        soup = BeautifulSoup(html_body, "html.parser")
        # soup = BeautifulSoup(urllib.request.urlopen(url), "html.parser")
        title = soup.title
        if title is None:
            title_str = ""
        elif title.string is None:
            title_str = ""
        elif title.string == "":
            title_str = ""
        else:
            title_str = title.string.strip()

        # 获取icon hash
        icon_url = get_icon_url(html_body, url)
        http_request_return_str = http_request(counter, icon_url, fa1, fa2, fa3)
        if http_request_return_str == "continue":
            return
        else:
            icon_response = http_request_return_str
        icon_content = icon_response.content
        icon_hash = get_icon_hash(icon_content)

        # 从指纹库中匹配指纹
        for finger in fingers:
            method = finger["method"]
            location = finger["location"]
            keyword_list = finger["keyword"]
            cms = finger["cms"]
            if (method == "keyword") and (location == "title"):
                if (title is not None) and (title != ""):  # 如果title不为None且不为空，基于title判断指纹
                    if keyword_list[0].lower() in title:  # 编写小工具检测后发现，title中的关键字只有一个，不需要迭代
                        csv_url_list.append(url)
                        csv_status_code_list.append(status_code)
                        csv_title_list.append(title_str)
                        csv_cms_list.append(cms)
                        print_finger(counter, url, str(status_code), title_str, cms)
                        # return  # 跳出指纹识别
                    else:
                        continue  # 跳到指纹库中下一个指纹
                else:
                    csv_url_list.append(url)
                    csv_status_code_list.append(status_code)
                    csv_title_list.append("")
                    csv_cms_list.append("")
                    print_finger(counter, url, str(status_code), "", "")
                    # return  # 跳出指纹识别
            elif (method == "keyword") and (location == "header"):
                for keyword in keyword_list:
                    if keyword.lower() in headers_str:
                        csv_url_list.append(url)
                        csv_status_code_list.append(status_code)
                        csv_title_list.append(title_str)
                        csv_cms_list.append(cms)
                        print_finger(counter, url, str(status_code), title_str, cms)
                        # return  # 跳出指纹识别
                continue  # 跳到指纹库中下一个指纹
            elif (method == "keyword") and (location == "body"):
                if all(keyword.lower() in html_body for keyword in keyword_list):
                    csv_url_list.append(url)
                    csv_status_code_list.append(status_code)
                    csv_title_list.append(title_str)
                    csv_cms_list.append(cms)
                    print_finger(counter, url, str(status_code), title_str, cms)
                    # return  # 跳出指纹识别
                else:
                    continue  # 跳到指纹库中下一个指纹
            elif (method == "icon_hash") and (location == "body"):
                if keyword_list == icon_hash:  # icon_hash的关键字只有一个，不需要迭代
                    csv_url_list.append(url)
                    csv_status_code_list.append(status_code)
                    csv_title_list.append(title_str)
                    csv_cms_list.append(cms)
                    print_finger(counter, url, str(status_code), title_str, cms)
                    # return  # 跳出指纹识别
                else:
                    continue  # 跳到指纹库中下一个指纹
        csv_url_list.append(url)
        csv_status_code_list.append(status_code)
        csv_title_list.append("")
        csv_cms_list.append("")
        print_finger(counter, url, str(status_code), "", "")
        print()

    else:
        print(f"{counter} 目标 {url} html_body 为 None")


def http_request(counter, url, fa1, fa2, fa3):
    headers = get_headers()
    try:
        response = requests.get(url=url, headers=headers, timeout=10, verify=False, allow_redirects=False)
    except requests.exceptions.SSLError:
        print(f"{counter} not write to file, for debug 1 ---- 跟目标 {url} 建立SSL连接时报错")
        return "continue"
    except requests.exceptions.ConnectTimeout:
        print(f"{counter} 跟目标 {url} 建立连接超时")
        fa1.write(f"跟目标 {url} 建立连接超时\n")
        return "continue"
    except requests.exceptions.ReadTimeout:
        print(f"{counter} 跟目标 {url} 建立连接后读取数据超时")
        fa2.write(f"跟目标 {url} 建立连接后读取数据超时\n")
        return "continue"
    except requests.exceptions.ConnectionError:
        print(f"{counter} 跟目标 {url} 建立连接时 连接被重置 或 连接被拒绝 或 网络不可达")
        fa3.write(f"跟目标 {url} 建立连接时 连接被重置 或 连接被拒绝 或 网络不可达\n")
        return "continue"
    except Exception as e:
        print(f"{counter} not write to file, for debug 2 ---- 目标 {url} 报错 {e}")
        return "continue"
    return response


def finger_identify(q, fingers, fa1, fa2, fa3, csv_url_list, csv_status_code_list, csv_title_list, csv_cms_list):
    global counter
    global _3xx_url

    # with counter_lock:

    while True:
        if q.empty():
            return
        else:
            counter = "   "  # 最初是用作计数器
            url = q.get()
            # print(f"目标url: {url}")  # debug code
            http_request_return_str = http_request(counter, url, fa1, fa2, fa3)
            if http_request_return_str == "continue":
                continue
            else:
                response = http_request_return_str
                status_code = response.status_code
                # print(f"目标url status_code: {status_code}")  # debug code

            if (status_code == 200) or (status_code == 304) or (status_code == 401) or (status_code == 403) or (status_code == 404):
                finger_identify_core(counter, response, url, status_code, fa1, fa2, fa3, fingers, csv_url_list, csv_status_code_list, csv_title_list, csv_cms_list)

            elif (status_code == 301) or (status_code == 302) or (status_code == 303) or (status_code == 307) or (status_code == 308):
                redirect_url = _3xx_get_redirect_url(response, url)
                redirect_http_request_return_str = _3xx_http_request(counter, redirect_url, fa1, fa2, fa2)
                if redirect_http_request_return_str == "continue":
                    continue
                else:
                    redirect_response = redirect_http_request_return_str
                    redirect_status_code = redirect_response.status_code
                    # print(f"重定向url status_code: {redirect_status_code}")  # debug code

                if (redirect_status_code == 200) or (redirect_status_code == 304) or (redirect_status_code == 401) or (redirect_status_code == 403) or (redirect_status_code == 404):
                    finger_redirect_identify_core(counter, redirect_response, url, status_code, redirect_url, redirect_status_code, fa1, fa2, fa3, fingers, csv_url_list, csv_status_code_list, csv_title_list, csv_cms_list)

                elif (redirect_status_code == 400) or (redirect_status_code == 405) or (redirect_status_code == 412) or (redirect_status_code == 415) or (redirect_status_code == 426) or (redirect_status_code == 444):
                    _4xx_redirect_print(counter, url, status_code, redirect_url, redirect_status_code)

                elif (redirect_status_code == 500) or (redirect_status_code == 501) or (redirect_status_code == 502) or (redirect_status_code == 503) or (redirect_status_code == 530):
                    _5xx_redirect_print(counter, url, status_code, redirect_url, redirect_status_code)

                else:
                    print(f"{counter} 目标 {redirect_url} 返回状态码 {redirect_status_code}")

            elif (status_code == 400) or (status_code == 405) or (status_code == 412) or (status_code == 415) or (status_code == 426) or (status_code == 444):
                _4xx_print(counter, url, status_code)

            elif (status_code == 500) or (status_code == 501) or (status_code == 502) or (status_code == 503) or (status_code == 530):
                _5xx_print(counter, url, status_code)

            else:
                print(f"{counter} 目标 {url} 返回状态码 {status_code}")


def usage():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", type=str,
                        help="要识别的url，例如：python3 RuiningFinger.py -u http://www.baidu.com", required=False)
    parser.add_argument("-f", "--file", dest="filename", type=str,
                        help="包含url的文件，每行一个，例如：python3 RuiningFinger.py -f 测试.txt", required=False)
    args = parser.parse_args()
    if args.url is not None:
        return args.url, "single"
    elif args.filename is not None:
        return args.filename, "multi"
    else:
        sys.exit("查看帮助：python3 RuiningFinger.py -h")


def banner(count):
    print()
    print()
    print('''
    ****************************************************************************
    红队Web打点--指纹识别
    
    当前指纹库共计：{}个指纹

    Author: ybdt
    ****************************************************************************
    '''.format(count))
    print()
    print()


def main():
    # Output banner
    with open("RuiningFinger.json", "r", encoding="utf-8") as fr:
        fingerprint = json.load(fr)
        fingers = fingerprint["fingerprint"]
    banner(len(fingers))

    # 获取用户输入
    arg, flag = usage()

    # 定义后面要用到的变量
    csv_url_list = []
    csv_status_code_list = []
    csv_title_list = []
    csv_cms_list = []

    # 多个URL
    if flag == "multi":
        filename = arg
        output_name = time.strftime("%Y年%m月%d日-%H时%M分%S秒", time.localtime())
        root_path = os.getcwd()
        url_file_path = os.path.join(root_path, filename)
        output_dir_path = os.path.join(root_path, output_name)
        os.mkdir(output_dir_path)
        os.chdir(output_dir_path)
        connection_timeout_path = os.path.join(output_dir_path, output_name + "-ConnectionTimeout.txt")
        read_timeout_path = os.path.join(output_dir_path, output_name + "-ReadTimeout.txt")
        connection_error_path = os.path.join(output_dir_path, output_name + "-ConnectionError.txt")
        fa1 = open(connection_timeout_path, "a")
        fa2 = open(read_timeout_path, "a")
        fa3 = open(connection_error_path, "a")

        url_list = []
        with open(url_file_path, "r") as fr:
            lines = fr.readlines()
            for line in lines:
                line = line.strip()
                url_list.append(line)
        print("目标共计：{}个".format(len(url_list)))
        q = queue.Queue()
        for url in url_list:
            q.put(url)
        threads_num = 30
        threads = []
        for i in range(threads_num):
            t = threading.Thread(target=finger_identify, args=(q, fingers, fa1, fa2, fa3, csv_url_list, csv_status_code_list, csv_title_list, csv_cms_list))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        csv_filename = output_name + ".csv"
        csv_data = {"URL": csv_url_list, "Status Code": csv_status_code_list, "Title": csv_title_list, "CMS": csv_cms_list}
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_filename, index=False)

    # 单个URL
    elif flag == "single":
        url = arg
        output_name = time.strftime("%Y年%m月%d日-%H时%M分%S秒", time.localtime())
        root_path = os.getcwd()
        output_dir_path = os.path.join(root_path, output_name)
        os.mkdir(output_dir_path)
        os.chdir(output_dir_path)
        connection_timeout_path = os.path.join(output_dir_path, output_name + "-ConnectionTimeout.txt")
        read_timeout_path = os.path.join(output_dir_path, output_name + "-ReadTimeout.txt")
        connection_error_path = os.path.join(output_dir_path, output_name + "-ConnectionError.txt")
        fa1 = open(connection_timeout_path, "a")
        fa2 = open(read_timeout_path, "a")
        fa3 = open(connection_error_path, "a")
        q = queue.Queue()
        q.put(url)
        finger_identify(q, fingers, fa1, fa2, fa3, csv_url_list, csv_status_code_list, csv_title_list, csv_cms_list)

    fa1.close()
    fa2.close()
    fa3.close()


if __name__ == "__main__":
    main()
