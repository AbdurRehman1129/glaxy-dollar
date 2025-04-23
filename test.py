import requests
import time
import random

# Download and parse the proxy list from Webshare
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

def use_website(random_user_agent, proxy):
    url = "https://www.glaxydollars.com.pk/login"
    
    headers = {
        "User-Agent": random_user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        session = requests.Session()
        print("Using proxy:", proxy)

        session.proxies.update(proxy)

        # Initial request
        response = session.get(url, headers=headers, timeout=10)
        
        if "Please wait" in response.text:
            print("Waiting for challenge...")
            time.sleep(3)
            response = session.get(url, headers=headers, timeout=10)

        xsrf_token = session.cookies.get('XSRF-TOKEN')
        galaxy_session = session.cookies.get('glaxy_dollars_pro_session')

        return {
            'XSRF-TOKEN': xsrf_token,
            'glaxy_dollars_pro_session': galaxy_session
        }
    except Exception as e:
        print(f"Request failed with proxy {proxy}: {e}")
        return None

# Main usage
if __name__ == "__main__":
    random_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    proxies = get_proxies()
    
    if proxies:
        chosen_proxy = random.choice(proxies)

        cookies = use_website(random_user_agent, chosen_proxy)
        if cookies:
            print("Cookies retrieved:", cookies)
        else:
            print("Failed to get cookies.")
    else:
        print("No proxies available.")
