import requests
from fake_useragent import UserAgent
import html
import json
import time
import re
import os
from datetime import datetime, timedelta
from urllib.parse import unquote

# ======================
# HEROKU FIXES
# ======================
if 'DYNO' in os.environ:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ======================
# SESSION MANAGER
# ======================
class GlaxySession:
    def __init__(self):
        self.session = requests.Session()
        self.user_agent = self._get_user_agent()
        self.xsrf_token = None
        self.pro_session = None
        
    def _get_user_agent(self):
        if 'DYNO' in os.environ:  # Running on Heroku
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        return UserAgent().random
    
    def update_cookies(self):
        self.session.cookies.update({
            "XSRF-TOKEN": self.xsrf_token,
            "glaxy_dollars_pro_session": self.pro_session
        })

# ======================
# CORE FUNCTIONS
# ======================
def access_login_page(gsession):
    url = "https://www.glaxydollars.com.pk/login"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": gsession.user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.glaxydollars.com.pk/user/dashboard",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=0, i"
    }
    
    try:
        response = gsession.session.get(url, headers=headers, verify=False)
        
        if response.status_code != 200:
            return {"error": f"Login page failed with status {response.status_code}"}
        
        # Extract livewire token
        livewire_token = None
        if "window.livewire_token" in response.text:
            match = re.search(r"window\.livewire_token\s*=\s*'([^']+)'", response.text)
            if match:
                livewire_token = match.group(1)
        
        # Extract fingerprint data
        fingerprint_id = checksum = htmlhash = None
        if 'wire:initial-data="' in response.text:
            match = re.search(r'wire:initial-data="({.+?})"', response.text)
            if match:
                try:
                    data = json.loads(html.unescape(match.group(1)))
                    fingerprint_id = data.get("fingerprint", {}).get("id")
                    checksum = data.get("serverMemo", {}).get("checksum")
                    htmlhash = data.get("serverMemo", {}).get("htmlHash")
                except json.JSONDecodeError:
                    pass
        
        # Update session cookies
        gsession.xsrf_token = response.cookies.get("XSRF-TOKEN")
        gsession.pro_session = response.cookies.get("glaxy_dollars_pro_session")
        gsession.update_cookies()
        
        return {
            "livewire_token": livewire_token,
            "fingerprint_id": fingerprint_id,
            "checksum": checksum,
            "htmlhash": htmlhash,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": f"Login page error: {str(e)}"}

def send_login_data(gsession, login_data, username, password):
    url = "https://www.glaxydollars.com.pk/livewire/message/user.auth.user-login"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Content-Length": "589",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "X-Csrf-Token": login_data['livewire_token'],
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": gsession.user_agent,
        "Accept": "text/html, application/xhtml+xml",
        "Content-Type": "application/json",
        "X-Livewire": "true",
        "Origin": "https://www.glaxydollars.com.pk",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.glaxydollars.com.pk/login",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=1, i"
    }
    
    payload = {
        "fingerprint": {
            "id": login_data['fingerprint_id'],
            "name": "user.auth.user-login",
            "locale": "en",
            "path": "login",
            "method": "GET",
            "v": "acj"
        },
        "serverMemo": {
            "children": [],
            "errors": [],
            "htmlHash": login_data['htmlhash'],
            "data": {"showPass": True, "email": None, "password": None},
            "dataMeta": [],
            "checksum": login_data['checksum']
        },
        "updates": [
            {
                "type": "syncInput",
                "payload": {
                    "id": "4xpj",
                    "name": "password",
                    "value": password
                }
            },
            {
                "type": "syncInput",
                "payload": {
                    "id": "oz1f",
                    "name": "email",
                    "value": username
                }
            },
            {
                "type": "callMethod",
                "payload": {
                    "id": "eupy",
                    "method": "login",
                    "params": []
                }
            }
        ]
    }
    
    try:
        response = gsession.session.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            gsession.xsrf_token = response.cookies.get("XSRF-TOKEN")
            gsession.pro_session = response.cookies.get("glaxy_dollars_pro_session")
            gsession.update_cookies()
            return {"status": "success"}
        
        return {"error": f"Login failed with status {response.status_code}"}
    except Exception as e:
        return {"error": f"Login request failed: {str(e)}"}

def access_dashboard(gsession):
    url = "https://www.glaxydollars.com.pk/user/dashboard"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": gsession.user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.glaxydollars.com.pk/login",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=0, i"
    }
    
    try:
        response = gsession.session.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            gsession.xsrf_token = response.cookies.get("XSRF-TOKEN")
            gsession.pro_session = response.cookies.get("glaxy_dollars_pro_session")
            gsession.update_cookies()
            
            # Extract livewire token
            livewire_token = None
            if "window.livewire_token" in response.text:
                match = re.search(r"window\.livewire_token\s*=\s*'([^']+)'", response.text)
                if match:
                    livewire_token = match.group(1)
            
            return {
                "status": "success",
                "livewire_token": livewire_token
            }
        
        return {"error": f"Dashboard access failed with status {response.status_code}"}
    except Exception as e:
        return {"error": f"Dashboard access failed: {str(e)}"}

def access_ads_page(gsession):
    url = "https://www.glaxydollars.com.pk/user/ads/video"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": gsession.user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.glaxydollars.com.pk/user/dashboard",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=0, i"
    }
    
    try:
        response = gsession.session.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            gsession.xsrf_token = response.cookies.get("XSRF-TOKEN")
            gsession.pro_session = response.cookies.get("glaxy_dollars_pro_session")
            gsession.update_cookies()
            
            # Extract video info
            video_number = youtube_url = None
            video_match = re.search(r'<span class="text-danger fw-bold fs-1">Video\s*(\d+)</span>', response.text)
            if video_match:
                video_number = video_match.group(1)
            
            youtube_match = re.search(r'src="(https?://www\.youtube\.com/embed/[^"]+)"', response.text)
            if youtube_match:
                youtube_url = unquote(youtube_match.group(1)).replace("&amp;", "&")
            
            # Extract Livewire data
            fingerprint = checksum = html_hash = timestamp = user_id = user_balance_id = None
            mb5_div_match = re.search(r'<div class="mb-5 p-3">(.*?)</div>\s*</div>', response.text, re.DOTALL)
            if mb5_div_match:
                wire_data_match = re.search(r'wire:initial-data="({.+?})"', mb5_div_match.group(1))
                if wire_data_match:
                    try:
                        wire_data = json.loads(wire_data_match.group(1).replace('&quot;', '"'))
                        fingerprint = wire_data.get("fingerprint", {}).get("id")
                        checksum = wire_data.get("serverMemo", {}).get("checksum")
                        html_hash = wire_data.get("serverMemo", {}).get("htmlHash")
                        timestamp = wire_data.get("serverMemo", {}).get("data", {}).get("show_time")
                        
                        models = wire_data.get("serverMemo", {}).get("dataMeta", {}).get("models", {})
                        user_id = models.get("user", {}).get("id")
                        user_balance_id = models.get("user_balance", {}).get("id")
                        
                        if not youtube_url:
                            youtube_url = wire_data.get("serverMemo", {}).get("data", {}).get("ad_link")
                    except json.JSONDecodeError:
                        pass
            
            if not video_number:
                return {"status": "complete", "message": "No more videos available"}
            
            return {
                "status": "success",
                "video_number": video_number,
                "youtube_url": youtube_url,
                "fingerprint": fingerprint,
                "checksum": checksum,
                "html_hash": html_hash,
                "timestamp": timestamp,
                "user_id": user_id,
                "user_balance_id": user_balance_id
            }
        
        return {"error": f"Ads page failed with status {response.status_code}"}
    except Exception as e:
        return {"error": f"Ads page access failed: {str(e)}"}

def submit_ad(gsession, ad_data):
    url = "https://www.glaxydollars.com.pk/livewire/message/user.ads.video-ads"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Content-Length": "878",
        "X-Csrf-Token": ad_data['livewire_token'],
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": gsession.user_agent,
        "Accept": "text/html, application/xhtml+xml",
        "Content-Type": "application/json",
        "X-Livewire": "true",
        "Origin": "https://www.glaxydollars.com.pk",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.glaxydollars.com.pk/user/ads/video",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=1, i"
    }
    
    payload = {
        "fingerprint": {
            "id": ad_data['fingerprint'],
            "name": "user.ads.video-ads",
            "locale": "en",
            "path": "user/ads/video",
            "method": "GET",
            "v": "acj"
        },
        "serverMemo": {
            "children": [],
            "errors": [],
            "htmlHash": ad_data['html_hash'],
            "data": {
                "user": [], 
                "user_balance": [],  
                "watch_time": 5,
                "ad_limit": 20,
                "ad_count": None, 
                "show_time": ad_data['timestamp'],
                "ad_link": ad_data['youtube_url'],
                "freezed": False
            },
            "dataMeta": {
                "models": {
                    "user": {
                        "class": "App\\Models\\User",
                        "id": ad_data['user_id'],
                        "relations": ["Package"],
                        "connection": "mysql",
                        "collectionClass": None
                    },
                    "user_balance": {
                        "class": "App\\Models\\UserBalance",
                        "id": ad_data['user_balance_id'],
                        "relations": [],
                        "connection": "mysql",
                        "collectionClass": None
                    }
                },
                "dates": {
                    "show_time": "carbon"
                }
            },
            "checksum": ad_data['checksum']
        },
        "updates": [
            {
                "type": "callMethod",
                "payload": {
                    "id": "93u2",  
                    "method": "nextAD",
                    "params": []
                }
            }
        ]
    }
    
    try:
        response = gsession.session.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            gsession.xsrf_token = response.cookies.get("XSRF-TOKEN")
            gsession.pro_session = response.cookies.get("glaxy_dollars_pro_session")
            gsession.update_cookies()
            return {"status": "success", "message": "Ad submitted successfully"}
        
        return {"error": f"Ad submission failed with status {response.status_code}"}
    except Exception as e:
        return {"error": f"Ad submission failed: {str(e)}"}

def access_typing_page(gsession):
    url = "https://www.glaxydollars.com.pk/user/ads/typing-task"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": gsession.user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.glaxydollars.com.pk/user/dashboard",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=0, i"
    }
    
    try:
        response = gsession.session.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            gsession.xsrf_token = response.cookies.get("XSRF-TOKEN")
            gsession.pro_session = response.cookies.get("glaxy_dollars_pro_session")
            gsession.update_cookies()
            
            # Extract task info
            task_number = None
            task_match = re.search(r'<span class="text-danger fw-bold fs-1">Typing Task\s*(\d+)</span>', response.text)
            if task_match:
                task_number = task_match.group(1)
            
            # Extract Livewire data
            fingerprint = checksum = html_hash = timestamp = user_id = user_balance_id = article_ad_id = None
            mb5_div_match = re.search(r'<div class="mb-5 p-3">(.*?)</div>\s*</div>', response.text, re.DOTALL)
            if mb5_div_match:
                wire_data_match = re.search(r'wire:initial-data="({.+?})"', mb5_div_match.group(1))
                if wire_data_match:
                    try:
                        wire_data = json.loads(wire_data_match.group(1).replace('&quot;', '"'))
                        fingerprint = wire_data.get("fingerprint", {}).get("id")
                        checksum = wire_data.get("serverMemo", {}).get("checksum")
                        html_hash = wire_data.get("serverMemo", {}).get("htmlHash")
                        timestamp = wire_data.get("serverMemo", {}).get("data", {}).get("show_time")
                        
                        models = wire_data.get("serverMemo", {}).get("dataMeta", {}).get("models", {})
                        user_id = models.get("user", {}).get("id")
                        user_balance_id = models.get("user_balance", {}).get("id")
                        article_ad_id = models.get("article_ad", {}).get("id")
                    except json.JSONDecodeError:
                        pass
            
            if not task_number:
                return {"status": "complete", "message": "No more typing tasks available"}
            
            return {
                "status": "success",
                "task_number": task_number,
                "fingerprint": fingerprint,
                "checksum": checksum,
                "html_hash": html_hash,
                "timestamp": timestamp,
                "user_id": user_id,
                "user_balance_id": user_balance_id,
                "article_ad_id": article_ad_id
            }
        
        return {"error": f"Typing page failed with status {response.status_code}"}
    except Exception as e:
        return {"error": f"Typing page access failed: {str(e)}"}

def submit_typing_task(gsession, task_data):
    url = "https://www.glaxydollars.com.pk/livewire/message/user.ads.article-ads"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Content-Length": "933",
        "X-Csrf-Token": task_data['livewire_token'],
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": gsession.user_agent,
        "Accept": "text/html, application/xhtml+xml",
        "Content-Type": "application/json",
        "X-Livewire": "true",
        "Origin": "https://www.glaxydollars.com.pk",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.glaxydollars.com.pk/user/ads/typing-task",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=1, i"
    }
    
    payload = {
        "fingerprint": {
            "id": task_data['fingerprint'],
            "name": "user.ads.article-ads",
            "locale": "en",
            "path": "user/ads/typing-task",
            "method": "GET",
            "v": "acj"
        },
        "serverMemo": {
            "children": [],
            "errors": [],
            "htmlHash": task_data['html_hash'],
            "data": {
                "user": [], 
                "user_balance": [],  
                "watch_time": 5,
                "ad_limit": 20,
                "ad_count": None, 
                "show_time": task_data['timestamp'],
                "article_ad": [],
                "freezed": False
            },
            "dataMeta": {
                "models": {
                    "user": {
                        "class": "App\\Models\\User",
                        "id": task_data['user_id'],
                        "relations": ["Package"],
                        "connection": "mysql",
                        "collectionClass": None
                    },
                    "user_balance": {
                        "class": "App\\Models\\UserBalance",
                        "id": task_data['user_balance_id'],
                        "relations": [],
                        "connection": "mysql",
                        "collectionClass": None
                    },
                    "article_ad": {
                        "class": "App\\Models\\AdArticle",
                        "id": task_data['article_ad_id'],
                        "relations": [],
                        "connection": "mysql",
                        "collectionClass": None
                    }
                },
                "dates": {
                    "show_time": "carbon"
                }
            },
            "checksum": task_data['checksum']
        },
        "updates": [
            {
                "type": "callMethod",
                "payload": {
                    "id": "sc1p",
                    "method": "nextAD",
                    "params": []
                }
            }
        ]
    }
    
    try:
        response = gsession.session.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            gsession.xsrf_token = response.cookies.get("XSRF-TOKEN")
            gsession.pro_session = response.cookies.get("glaxy_dollars_pro_session")
            gsession.update_cookies()
            return {"status": "success", "message": "Typing task submitted successfully"}
        
        return {"error": f"Typing task submission failed with status {response.status_code}"}
    except Exception as e:
        return {"error": f"Typing task submission failed: {str(e)}"}

# ======================
# MAIN AUTOMATION FLOW
# ======================
def automate(username, password):
    print(f"🚀 Starting automation for account: {username}")
    
    # Initialize session
    gsession = GlaxySession()
    
    # Step 1: Access login page
    print("🔒 Accessing login page...")
    login_page_data = access_login_page(gsession)
    if "error" in login_page_data:
        print(f"❌ Error: {login_page_data['error']}")
        return False
    
    # Step 2: Perform login
    print("🔑 Logging in...")
    login_result = send_login_data(gsession, login_page_data, username, password)
    if "error" in login_result:
        print(f"❌ Login failed: {login_result['error']}")
        return False
    
    # Step 3: Access dashboard
    print("📊 Accessing dashboard...")
    dashboard_result = access_dashboard(gsession)
    if "error" in dashboard_result:
        print(f"❌ Dashboard access failed: {dashboard_result['error']}")
        return False
    
    # Process video ads
    print("🎥 Processing video ads...")
    while True:
        ads_result = access_ads_page(gsession)
        
        if "error" in ads_result:
            print(f"❌ Ads page error: {ads_result['error']}")
            break
            
        if ads_result.get("status") == "complete":
            print("✅ All video ads processed")
            break
            
        print(f"📹 Processing video {ads_result.get('video_number')}...")
        
        # Prepare ad submission data
        ad_data = {
            "livewire_token": dashboard_result.get("livewire_token"),
            "youtube_url": ads_result.get("youtube_url"),
            "fingerprint": ads_result.get("fingerprint"),
            "checksum": ads_result.get("checksum"),
            "html_hash": ads_result.get("html_hash"),
            "timestamp": ads_result.get("timestamp"),
            "user_id": ads_result.get("user_id"),
            "user_balance_id": ads_result.get("user_balance_id")
        }
        
        # Submit ad
        submit_result = submit_ad(gsession, ad_data)
        if "error" in submit_result:
            print(f"❌ Ad submission failed: {submit_result['error']}")
        else:
            print(f"✅ {submit_result.get('message')}")
        
        time.sleep(5)  # Delay between ads
    
    # Process typing tasks
    print("⌨️ Processing typing tasks...")
    while True:
        typing_result = access_typing_page(gsession)
        
        if "error" in typing_result:
            print(f"❌ Typing page error: {typing_result['error']}")
            break
            
        if typing_result.get("status") == "complete":
            print("✅ All typing tasks processed")
            break
            
        print(f"📝 Processing task {typing_result.get('task_number')}...")
        
        # Prepare task submission data
        task_data = {
            "livewire_token": dashboard_result.get("livewire_token"),
            "fingerprint": typing_result.get("fingerprint"),
            "checksum": typing_result.get("checksum"),
            "html_hash": typing_result.get("html_hash"),
            "timestamp": typing_result.get("timestamp"),
            "user_id": typing_result.get("user_id"),
            "user_balance_id": typing_result.get("user_balance_id"),
            "article_ad_id": typing_result.get("article_ad_id")
        }
        
        # Submit task
        submit_result = submit_typing_task(gsession, task_data)
        if "error" in submit_result:
            print(f"❌ Task submission failed: {submit_result['error']}")
        else:
            print(f"✅ {submit_result.get('message')}")
        
        time.sleep(5)  # Delay between tasks
    
    print("🎉 Automation completed successfully!")
    return True

# ======================
# ENTRY POINT
# ======================
# [Previous imports and class definitions remain the same...]

def process_account(username, password):
    print(f"\n🔁 Processing account: {username}")
    gsession = GlaxySession()
    
    # Login flow
    login_page_data = access_login_page(gsession)
    if "error" in login_page_data:
        print(f"❌ Login page error: {login_page_data['error']}")
        return False
        
    login_result = send_login_data(gsession, login_page_data, username, password)
    if "error" in login_result:
        print(f"❌ Login failed: {login_result['error']}")
        return False
    
    # [Rest of your automation flow remains the same...]
    return True

if __name__ == "__main__":
    # Load multiple accounts
    accounts = []
    
    if 'DYNO' in os.environ:  # Heroku - use environment variables
        # Format: "user1:pass1,user2:pass2,user3:pass3"
        accounts_str = os.getenv('ACCOUNTS')
        if not accounts_str:
            print("❌ Error: Please set ACCOUNTS environment variable")
            exit()
        accounts = [acc.split(":") for acc in accounts_str.split(",")]
    else:  # Local - use creds.txt
        try:
            with open("creds.txt", "r") as f:
                accounts = [line.strip().split(":", 1) for line in f if ":" in line]
        except Exception as e:
            print(f"❌ Error reading credentials: {str(e)}")
            exit()

    if not accounts:
        print("❌ No accounts found")
        exit()

    print(f"👥 Found {len(accounts)} accounts to process")
    
    # Process each account
    for username, password in accounts:
        success = process_account(username, password)
        status = "✅ Success" if success else "❌ Failed"
        print(f"{status} - Account: {username}")
        
        # Delay between accounts (avoid rate limiting)
        if accounts.index((username, password)) < len(accounts) - 1:
            print("⏳ Waiting 30 seconds before next account...")
            time.sleep(30)