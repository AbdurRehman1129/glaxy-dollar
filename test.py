import requests
import time
import random
import json
import html

def get_proxies():
    proxy_url = "https://proxy.webshare.io/api/v2/proxy/list/download/hlezaktorylkvdogejmezzswxnzfsfqpdrzsigbh/-/any/username/direct/-/"
    try:
        response = requests.get(proxy_url)
        proxies_raw = response.text.strip().split('\n')
        proxies = []
        for proxy in proxies_raw:
            # Format: ip:port:user:pass
            parts = proxy.strip().split(":")
            if len(parts) == 4:
                ip, port, user, pwd = parts
                proxy_dict = {
                    "http": f"http://{user}:{pwd}@{ip}:{port}",
                    "https": f"http://{user}:{pwd}@{ip}:{port}",
                }
                proxies.append(proxy_dict)
        return proxies
    except Exception as e:
        print(f"Error downloading proxies: {e}")
        return []

def access_login_page(random_user_agent, glaxy_dollar_pro_session_use, xsrf_token_use):
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
        "XSRF-TOKEN":xsrf_token_use,
        "glaxy_dollars_pro_session": glaxy_dollar_pro_session_use
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
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=10)
            with open("response.html", "w", encoding="utf-8") as file:
                file.write(response.text)
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

# Main usage
if __name__ == "__main__":
    random_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    result_access = access_login_page(random_user_agent, "glaxy_dollar_pro_session_use", "xsrf_token_use")
    
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