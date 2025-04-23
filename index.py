import requests
from fake_useragent import UserAgent
import html
import json
import time
import re
from datetime import datetime, timedelta
from urllib.parse import unquote

def access_login_page(random_user_agent):
    """
    Sends a GET request to the Glaxy Dollars login page with specific headers and cookies.
    Extracts livewire_token, fingerprint_id, checksum, and cookies from the response.
    Returns a dictionary containing the extracted data.
    """
    url = "https://www.glaxydollars.com.pk/login"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": random_user_agent,
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
    
    cookies = {
        "XSRF-TOKEN": "abcd",
        "glaxy_dollars_pro_session": "abcd"
    }
    
    def is_network_issue(status_code):
        # Common network-related status codes
        return status_code in [408, 429, 500, 502, 503, 504]

    max_retries = 3
    retry_delay = 5  # seconds
    retries = 0

    while retries < max_retries:
        try:
            # Sending GET request with headers and cookies
            response = requests.get(url, headers=headers, cookies=cookies)
            
            if response.status_code != 200:
                if is_network_issue(response.status_code):
                    print(f"Network issue detected (status code: {response.status_code}). Retrying in {retry_delay} seconds...")
                    retries += 1
                    time.sleep(retry_delay)
                    continue
                return {
                    "status_code": response.status_code,
                    "error": "Failed to access the login page.",
                    "response_headers": response.headers
                }
            
            # Extract livewire_token
            livewire_token = None
            if "window.livewire_token" in response.text:
                start_index = response.text.find("window.livewire_token = '") + len("window.livewire_token = '")
                end_index = response.text.find("';", start_index)
                livewire_token = response.text[start_index:end_index]
            
            # Extract fingerprint id and checksum
            fingerprint_id = None
            checksum = None
            htmlhash = None
            if 'wire:initial-data="' in response.text:
                start_index = response.text.find('wire:initial-data="') + len('wire:initial-data="')
                end_index = response.text.find('"', start_index)
                initial_data = response.text[start_index:end_index]
                
                decoded_data = html.unescape(initial_data)
                
                try:
                    data_json = json.loads(decoded_data)
                    fingerprint_id = data_json.get("fingerprint", {}).get("id")
                    checksum = data_json.get("serverMemo", {}).get("checksum")
                    htmlhash = data_json.get("serverMemo", {}).get("htmlHash")
                except json.JSONDecodeError:
                    pass
            
            # Extract cookies
            glaxy_dollar_pro_session = response.cookies.get("glaxy_dollars_pro_session")
            xsrf_token = response.cookies.get("XSRF-TOKEN")
            
            return {
                "status_code": response.status_code,
                "livewire_token": livewire_token,
                "fingerprint_id": fingerprint_id,
                "checksum": checksum,
                "glaxy_dollar_pro_session": glaxy_dollar_pro_session,
                "xsrf_token": xsrf_token,
                "htmlhash": htmlhash
            }
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            retries += 1
            time.sleep(retry_delay)

    print("Max retries reached. Unable to complete the request.")
    return {"error": "Max retries reached. Unable to complete the request."}

def send_login_data(xsrf_token, pro_session, csrf_token, fingerprint, checksum, random_user_agent,htmlhash, username, password):
    url = "https://www.glaxydollars.com.pk/livewire/message/user.auth.user-login"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Cookie": f"XSRF-TOKEN={xsrf_token}; glaxy_dollars_pro_session={pro_session}",
        "Content-Length": "589",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "X-Csrf-Token": csrf_token,
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": random_user_agent,
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
            "id": fingerprint,
            "name": "user.auth.user-login",
            "locale": "en",
            "path": "login",
            "method": "GET",
            "v": "acj"
        },
        "serverMemo": {
            "children": [],
            "errors": [],
            "htmlHash": htmlhash,
            "data": {
                "showPass": True,
                "email": None,
                "password": None
            },
            "dataMeta": [],
            "checksum": checksum
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
    
    def is_network_issue(status_code):
        # Common network-related status codes
        return status_code in [408, 429, 500, 502, 503, 504]

    try:
        max_retries = 3
        retry_delay = 5  # seconds
        retries = 0

        while retries < max_retries:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                # Extract cookies
                xsrf_token = response.cookies.get("XSRF-TOKEN")
                pro_session = response.cookies.get("glaxy_dollars_pro_session")
    
                return {
                    "xsrf_token": xsrf_token,
                    "pro_session": pro_session,
                }
            elif is_network_issue(response.status_code):
                print(f"Network issue detected (status code: {response.status_code}). Retrying in {retry_delay} seconds...")
                retries += 1
                time.sleep(retry_delay)
            else:
                print(f"Failed with status code: {response.status_code}")
                return None
        print("Max retries reached. Unable to complete the request.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def access_dashboard(random_user_agent, pro_session, xsrf_token):
    url = "https://www.glaxydollars.com.pk/user/dashboard"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": random_user_agent,
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
    
    cookies = {
        "XSRF-TOKEN": xsrf_token,
        "glaxy_dollars_pro_session": pro_session
    }
    
    def is_network_issue(status_code):
        # Common network-related status codes
        return status_code in [408, 429, 500, 502, 503, 504]

    max_retries = 3
    retry_delay = 5  # seconds
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies
            )
            if response.status_code == 200:
                xsrf_token = response.cookies.get("XSRF-TOKEN")
                glaxy_dollars_pro_session = response.cookies.get("glaxy_dollars_pro_session")
                return {
                    "xsrf_token": xsrf_token,
                    "glaxy_dollars_pro_session": glaxy_dollars_pro_session,
                }
            elif is_network_issue(response.status_code):
                print(f"Network issue detected (status code: {response.status_code}). Retrying in {retry_delay} seconds...")
                retries += 1
                time.sleep(retry_delay)
            else:
                print(f"Request failed with status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            retries += 1
            time.sleep(retry_delay)

    print("Max retries reached. Unable to complete the request.")
    return None

def access_ads_page(random_user_agent, xsrf_token, pro_session):
    url = "https://www.glaxydollars.com.pk/user/ads/video"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": random_user_agent,
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
    
    cookies = {
        "XSRF-TOKEN": xsrf_token,
        "glaxy_dollars_pro_session": pro_session
    }
    
    def is_retryable_error(status_code):
        return status_code in [408, 429, 500, 502, 503, 504]

    max_retries = 3
    retry_delay = 5
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                timeout=30
            )
            
            if response.status_code == 200:
                response_cookies = response.cookies.get_dict()
                xsrf_token_new = response_cookies.get('XSRF-TOKEN', 'Not found in response cookies')
                pro_session_new = response_cookies.get('glaxy_dollars_pro_session', 'Not found in response cookies')
                
                # Find Livewire token
                livewire_token = 'Not found'
                livewire_match = re.search(r"window\.livewire_token\s*=\s*'([^']+)'", response.text)
                if livewire_match:
                    livewire_token = livewire_match.group(1)
                
                # Find YouTube video URL
                youtube_url = 'Not found'
                youtube_match = re.search(r'src="(https?://www\.youtube\.com/embed/[^"]+)"', response.text)
                if youtube_match:
                    youtube_url = unquote(youtube_match.group(1)).replace("&amp;", "&")
                
                # Find video number
                video_number = 'Not found'
                video_number_match = re.search(r'<span class="text-danger fw-bold fs-1">Video\s*(\d+)</span>', response.text)
                if video_number_match:
                    video_number = video_number_match.group(1)
                
                # Find the mb-5 p-3 div which contains the video ads component
                mb5_div_match = re.search(r'<div class="mb-5 p-3">(.*?)</div>\s*</div>', response.text, re.DOTALL)
                if mb5_div_match:
                    mb5_div_content = mb5_div_match.group(1)
                    # Extract wire:initial-data from this div
                    wire_data_match = re.search(r'wire:initial-data="({.+?})"', mb5_div_content)
                    if wire_data_match:
                        try:
                            wire_data = json.loads(wire_data_match.group(1).replace('&quot;', '"'))
                            
                            # Extract all required information
                            html_hash = wire_data.get('serverMemo', {}).get('htmlHash', 'Not found')
                            checksum = wire_data.get('serverMemo', {}).get('checksum', 'Not found')
                            fingerprint = wire_data.get('fingerprint', {}).get('id', 'Not found')
                            timestamp = wire_data.get('serverMemo', {}).get('data', {}).get('show_time', 'Not found')
                            
                            # If YouTube URL wasn't found earlier, try to get it from wire data
                            if youtube_url == 'Not found':
                                youtube_url = wire_data.get('serverMemo', {}).get('data', {}).get('ad_link', 'Not found')
                            
                            data_meta = wire_data.get('serverMemo', {}).get('dataMeta', {})
                            models = data_meta.get('models', {})
                            user_id = models.get('user', {}).get('id', 'Not found')
                            user_balance_id = models.get('user_balance', {}).get('id', 'Not found')
                            
                            return {
                                "status": "success",
                                "xsrf_token_new": xsrf_token_new,
                                "pro_session_new": pro_session_new,
                                "livewire_token": livewire_token,
                                "youtube_url": youtube_url,
                                "video_number": video_number,  # Added video number to response
                                "html_hash": html_hash,
                                "checksum": checksum,
                                "fingerprint": fingerprint,
                                "timestamp": timestamp,
                                "user_id": user_id,
                                "user_balance_id": user_balance_id,
                            }
                            
                        except json.JSONDecodeError as e:
                            print(f"Error parsing wire:initial-data: {e}")
                            return {
                                "status": "error",
                                "message": f"JSON parsing error: {str(e)}",
                                "response_text": response.text,
                                "youtube_url": youtube_url,
                                "video_number": video_number  # Added video number to error response
                            }
                    else:
                        error_msg = "Could not find wire:initial-data in the mb-5 p-3 div"
                        print(error_msg)
                        return {
                            "status": "error",
                            "message": error_msg,
                            "response_text": response.text,
                            "youtube_url": youtube_url,
                            "video_number": video_number  # Added video number to error response
                        }
                else:
                    error_msg = "Could not find the mb-5 p-3 div in the response"
                    print(error_msg)
                    return {
                        "status": "error",
                        "message": error_msg,
                        "response_text": response.text,
                        "youtube_url": youtube_url,
                        "video_number": video_number  # Added video number to error response
                    }
                
            elif is_retryable_error(response.status_code):
                print(f"Retryable error detected (status code: {response.status_code}). Retrying in {retry_delay} seconds...")
                retries += 1
                time.sleep(retry_delay)
                continue
            else:
                error_msg = f"Request failed with status code: {response.status_code}"
                print(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "status_code": response.status_code
                }
            
        except requests.exceptions.Timeout:
            print(f"Request timed out. Retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)
        except requests.exceptions.RequestException as e:
            print(f"Request exception occurred: {e}")
            retries += 1
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    return {
        "status": "error",
        "message": "Max retries reached. Unable to complete the request."
    }

def access_typing_page(random_user_agent, xsrf_token, pro_session):
    url = "https://www.glaxydollars.com.pk/user/ads/typing-task"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": random_user_agent,
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
    
    cookies = {
        "XSRF-TOKEN": xsrf_token,
        "glaxy_dollars_pro_session": pro_session
    }
    
    def is_retryable_error(status_code):
        return status_code in [408, 429, 500, 502, 503, 504]

    max_retries = 3
    retry_delay = 5
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(
                url,
                headers=headers,
                cookies=cookies,
                timeout=30
            )
            
            if response.status_code == 200:
                response_cookies = response.cookies.get_dict()
                xsrf_token_new = response_cookies.get('XSRF-TOKEN', 'Not found in response cookies')
                pro_session_new = response_cookies.get('glaxy_dollars_pro_session', 'Not found in response cookies')
                
                # Find Livewire token
                livewire_token = 'Not found'
                livewire_match = re.search(r"window\.livewire_token\s*=\s*'([^']+)'", response.text)
                if livewire_match:
                    livewire_token = livewire_match.group(1)
                
                # Find typing task number
                task_number = 'Not found'
                task_number_match = re.search(r'<span class="text-danger fw-bold fs-1">Typing Task\s*(\d+)</span>', response.text)
                if task_number_match:
                    task_number = task_number_match.group(1)
                
                # Find the mb-5 p-3 div which contains the typing task component
                mb5_div_match = re.search(r'<div class="mb-5 p-3">(.*?)</div>\s*</div>', response.text, re.DOTALL)
                if mb5_div_match:
                    mb5_div_content = mb5_div_match.group(1)
                    # Extract wire:initial-data from this div
                    wire_data_match = re.search(r'wire:initial-data="({.+?})"', mb5_div_content)
                    if wire_data_match:
                        try:
                            wire_data = json.loads(wire_data_match.group(1).replace('&quot;', '"'))
                            
                            # Extract all required information
                            html_hash = wire_data.get('serverMemo', {}).get('htmlHash', 'Not found')
                            checksum = wire_data.get('serverMemo', {}).get('checksum', 'Not found')
                            fingerprint = wire_data.get('fingerprint', {}).get('id', 'Not found')
                            timestamp = wire_data.get('serverMemo', {}).get('data', {}).get('show_time', 'Not found')
                            
                            data_meta = wire_data.get('serverMemo', {}).get('dataMeta', {})
                            models = data_meta.get('models', {})
                            user_id = models.get('user', {}).get('id', 'Not found')
                            user_balance_id = models.get('user_balance', {}).get('id', 'Not found')
                            article_ad_id = models.get('article_ad', {}).get('id', 'Not found')
                            
                            return {
                                "status": "success",
                                "xsrf_token_new": xsrf_token_new,
                                "pro_session_new": pro_session_new,
                                "livewire_token": livewire_token,
                                "task_number": task_number,
                                "html_hash": html_hash,
                                "checksum": checksum,
                                "fingerprint": fingerprint,
                                "timestamp": timestamp,
                                "user_id": user_id,
                                "user_balance_id": user_balance_id,
                                "article_ad_id": article_ad_id  # Added this field
                            }
                            
                        except json.JSONDecodeError as e:
                            print(f"Error parsing wire:initial-data: {e}")
                            return {
                                "status": "error",
                                "message": f"JSON parsing error: {str(e)}",
                                "response_text": response.text,
                                "task_number": task_number
                            }
                    else:
                        error_msg = "Could not find wire:initial-data in the mb-5 p-3 div"
                        print(error_msg)
                        return {
                            "status": "error",
                            "message": error_msg,
                            "response_text": response.text,
                            "task_number": task_number
                        }
                else:
                    error_msg = "Could not find the mb-5 p-3 div in the response"
                    print(error_msg)
                    return {
                        "status": "error",
                        "message": error_msg,
                        "response_text": response.text,
                        "task_number": task_number
                    }
                
            elif is_retryable_error(response.status_code):
                print(f"Retryable error detected (status code: {response.status_code}). Retrying in {retry_delay} seconds...")
                retries += 1
                time.sleep(retry_delay)
                continue
            else:
                error_msg = f"Request failed with status code: {response.status_code}"
                print(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "status_code": response.status_code
                }
            
        except requests.exceptions.Timeout:
            print(f"Request timed out. Retrying in {retry_delay} seconds...")
            retries += 1
            time.sleep(retry_delay)
        except requests.exceptions.RequestException as e:
            print(f"Request exception occurred: {e}")
            retries += 1
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    return {
        "status": "error",
        "message": "Max retries reached. Unable to complete the request."
    }

def submit_ad(random_user_agent, xsrf_token, pro_session, youtube_url, htmlhash, fingerprint_id, checksum, user_id, user_balance_id, livewire_token,show_time):
    url = "https://www.glaxydollars.com.pk/livewire/message/user.ads.video-ads"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Content-Length": "878",
        "X-Csrf-Token": livewire_token,
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": random_user_agent,
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
        "Priority": "u=1, i",
        "Cookie": f"XSRF-TOKEN={xsrf_token}; glaxy_dollars_pro_session={pro_session}"
    }
    
    payload = {
        "fingerprint": {
            "id": fingerprint_id,
            "name": "user.ads.video-ads",
            "locale": "en",
            "path": "user/ads/video",
            "method": "GET",
            "v": "acj"
        },
        "serverMemo": {
            "children": [],
            "errors": [],
            "htmlHash": htmlhash,
            "data": {
                "user": [], 
                "user_balance": [],  
                "watch_time": 5,
                "ad_limit": 20,
                "ad_count": None, 
                "show_time": show_time,
                "ad_link": youtube_url,
                "freezed": False
            },
            "dataMeta": {
                "models": {
                    "user": {
                        "class": "App\\Models\\User",
                        "id": int(user_id),
                        "relations": ["Package"],
                        "connection": "mysql",
                        "collectionClass": None
                    },
                    "user_balance": {
                        "class": "App\\Models\\UserBalance",
                        "id": int(user_balance_id),
                        "relations": [],
                        "connection": "mysql",
                        "collectionClass": None
                    }
                },
                "dates": {
                    "show_time": "carbon"
                }
            },
            "checksum": checksum
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
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
      
        if response.status_code == 200:
            try:
                response_json = response.json()
                print("✅ Ad submitted successfully.")

                return response_json
            except json.JSONDecodeError:
                print("\nResponse Text:")
                print(response.text)
                return {"status": "error", "message": "Invalid JSON response", "text": response.text}
        else:
            print("\nError Response Text:")
            print(response.text)
            return {"status": "error", "status_code": response.status_code, "text": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest Exception: {str(e)}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"\nUnexpected Error: {str(e)}")
        return {"status": "error", "message": str(e)}

def submit_typing_task(random_user_agent, xsrf_token, pro_session, htmlhash, fingerprint_id, checksum, user_id, user_balance_id, livewire_token, show_time, article_ad_id):
    url = "https://www.glaxydollars.com.pk/livewire/message/user.ads.article-ads"
    
    headers = {
        "Host": "www.glaxydollars.com.pk",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Content-Length": "933",  # This should be calculated dynamically
        "X-Csrf-Token": livewire_token,
        "Sec-Ch-Ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": random_user_agent,
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
        "Priority": "u=1, i",
        "Cookie": f"XSRF-TOKEN={xsrf_token}; glaxy_dollars_pro_session={pro_session}"
    }
    
    payload = {
        "fingerprint": {
            "id": fingerprint_id,
            "name": "user.ads.article-ads",
            "locale": "en",
            "path": "user/ads/typing-task",
            "method": "GET",
            "v": "acj"
        },
        "serverMemo": {
            "children": [],
            "errors": [],
            "htmlHash": htmlhash,
            "data": {
                "user": [], 
                "user_balance": [],  
                "watch_time": 5,
                "ad_limit": 20,
                "ad_count": None, 
                "show_time": show_time,
                "article_ad": [],
                "freezed": False
            },
            "dataMeta": {
                "models": {
                    "user": {
                        "class": "App\\Models\\User",
                        "id": int(user_id),
                        "relations": ["Package"],
                        "connection": "mysql",
                        "collectionClass": None
                    },
                    "user_balance": {
                        "class": "App\\Models\\UserBalance",
                        "id": int(user_balance_id),
                        "relations": [],
                        "connection": "mysql",
                        "collectionClass": None
                    },
                    "article_ad": {
                        "class": "App\\Models\\AdArticle",
                        "id": int(article_ad_id),
                        "relations": [],
                        "connection": "mysql",
                        "collectionClass": None
                    }
                },
                "dates": {
                    "show_time": "carbon"
                }
            },
            "checksum": checksum
        },
        "updates": [
            {
                "type": "callMethod",
                "payload": {
                    "id": "sc1p",  # This appears to be a random ID, can be static or generated
                    "method": "nextAD",
                    "params": []
                }
            }
        ]
    }
    
    try:
        # Calculate actual content length
        payload_str = json.dumps(payload)
        headers["Content-Length"] = str(len(payload_str))
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print("✅ Typing task submitted successfully.")
                return response_json
            except json.JSONDecodeError:
                print("\nResponse Text:")
                print(response.text)
                return {"status": "error", "message": "Invalid JSON response", "text": response.text}
        else:
            print("\nError Response Text:")
            print(response.text)
            return {"status": "error", "status_code": response.status_code, "text": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest Exception: {str(e)}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"\nUnexpected Error: {str(e)}")
        return {"status": "error", "message": str(e)}

def automate(username,password):
    ua = UserAgent()
    random_user_agent = ua.random
    result_access = access_login_page(random_user_agent)
    
    if "error" in result_access:
        print(result_access["error"])
    else:
        print("✅ Login page accessed successfully.")
        livewire_token_access = result_access.get('livewire_token')
        fingerprint_id_access = result_access.get('fingerprint_id')
        checksum_access = result_access.get('checksum')
        htmlhash_access = result_access.get('htmlhash')
        glaxy_dollar_pro_session_access = result_access.get('glaxy_dollar_pro_session')
        xsrf_token_access = result_access.get('xsrf_token')

        print("\n" + "-" * 50)
        print(f"livewire_token_access: {livewire_token_access}")
        print(f"fingerprint_id_access: {fingerprint_id_access}")
        print(f"checksum_access: {checksum_access}")
        print(f"htmlhash_access: {htmlhash_access}")
        print(f"glaxy_dollar_pro_session_access: {glaxy_dollar_pro_session_access}")
        print(f"xsrf_token_access: {xsrf_token_access}")
        print("-" * 50 + "\n")
    result_login = send_login_data(xsrf_token_access, glaxy_dollar_pro_session_access, livewire_token_access, fingerprint_id_access, checksum_access, random_user_agent,htmlhash_access, username, password)
    if result_login:
        xsrf_token_login = result_login.get('xsrf_token')
        pro_session_login = result_login.get('pro_session')
        print("✅ Login data sent successfully.")
    else:
        print("❌ Failed to send login data.")

    result_dashboard = access_dashboard(random_user_agent, pro_session_login, xsrf_token_login)
    if result_dashboard:
        xsrf_token_dashboard = result_dashboard.get('xsrf_token')
        glaxy_dollars_pro_session_dashboard = result_dashboard.get('glaxy_dollars_pro_session')
        print("✅ Dashboard accessed successfully. ")

    else:
        print("❌ Failed to access the dashboard.")

    while True:
        result_ads = access_ads_page(random_user_agent, xsrf_token_dashboard, glaxy_dollars_pro_session_dashboard)
        if result_ads:
            xsrf_token_ads = result_ads.get('xsrf_token_new')
            pro_session_ads = result_ads.get('pro_session_new')
            livewire_token_ads = result_ads.get('livewire_token')
            youtube_url_ads = result_ads.get('youtube_url')
            html_hash_ads = result_ads.get('html_hash')
            checksum_ads = result_ads.get('checksum')
            fingerprint_ads = result_ads.get('fingerprint')
            user_id_ads = result_ads.get('user_id')
            user_balance_id_ads = result_ads.get('user_balance_id')
            show_time_ads = result_ads.get('timestamp')
            video_number_ads = result_ads.get('video_number')

            if video_number_ads == 'Not found':
                print("✅ All ads have been processed.")
                break

            print(f"✅ Ads page accessed successfully. Video Number: {video_number_ads}")

            submit_ad(random_user_agent, xsrf_token_ads, pro_session_ads, youtube_url_ads, html_hash_ads, fingerprint_ads, checksum_ads, user_id_ads, user_balance_id_ads, livewire_token_ads, show_time_ads)
            
        else:
            print("❌ Failed to access the ads page.")
            break
    
    while True:
        results_access_typing = access_typing_page(random_user_agent, xsrf_token_dashboard, glaxy_dollars_pro_session_dashboard)
        if results_access_typing:
            xsrf_token_typing = results_access_typing.get('xsrf_token_new')
            pro_session_typing = results_access_typing.get('pro_session_new')
            livewire_token_typing = results_access_typing.get('livewire_token')
            task_number_typing = results_access_typing.get('task_number')
            html_hash_typing = results_access_typing.get('html_hash')
            checksum_typing = results_access_typing.get('checksum')
            fingerprint_typing = results_access_typing.get('fingerprint')
            user_id_typing = results_access_typing.get('user_id')
            user_balance_id_typing = results_access_typing.get('user_balance_id')
            show_time_typing = results_access_typing.get('timestamp')
            article_ad_id_typing = results_access_typing.get('article_ad_id')
            if article_ad_id_typing == 'Not found':
                        print("✅ All tasks have been processed.")
                        break
                    
            print(f"✅ Typing page accessed successfully. Task Number: {task_number_typing}")
            submit_typing_task(random_user_agent, xsrf_token_typing, pro_session_typing, html_hash_typing, fingerprint_typing, checksum_typing, user_id_typing, user_balance_id_typing, livewire_token_typing, show_time_typing, article_ad_id_typing)

        else:
            print("❌ Failed to access the typing page.")

if __name__ == "__main__":
    with open("creds.txt", "r") as creds_file:
        for line in creds_file:
            if ":" in line:
                username, password = line.strip().split(":", 1)
                print(f"🔄 Processing account: {username}")
                automate(username, password)
                