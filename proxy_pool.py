import requests
import asyncio
import aiohttp
from datetime import datetime
import random


PROXY_URL = "https://www.kuaidaili.com/free/inha/"

TEST_PROXIES = [
    "114.239.147.86:9000",
    "121.237.148.66:3000",
    "112.114.97.11:8080"
]

TEST_URL = "https://movie.douban.com/top250"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 ",
    "Accept-Language" : "zh-CN,zh;q=0.9",
    "Referer": "https://www.douban.com/"
}

class MemoryProxyPool:
    def __init__(self):
        self.proxies = set()

    def add_proxy(self, proxy):
        self.proxies.add(proxy)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] proxy added: {proxy}")

    def proxies_count(self):
        return len(self.proxies)

    def random_proxy(self):
        if self.proxies :
            return random.choice(list(self.proxies))
        else :
            return None

    def clear_proxy(self):
        self.proxies.clear()

def crawl_free_proxy(url):
    proxies = []
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
            verify=False,
            cookies = {"sessionid": "123456789"},  # 模拟登录cookie，避开基础反爬
            allow_redirects = True
        )
        response.encoding = response.apparent_encoding
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_list = soup.select("table.table tbody tr")
        print(f"解析到 {len(tr_list)} 行数据")
        for tr in tr_list:
            td_list = tr.find_all("td")
            if len(td_list) >=2 :
                ip = td_list[0].text.strip()
                port = td_list[1].text.strip()
                if ip and port :
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] proxy added: {len(proxies)}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] proxy failed: {str(e)}")
    return proxies

async def verify_single_proxy(session,proxy,test_url,proxy_pool):
    proxy_str = f"http://{proxy}"

    try:
        async with session.get(
            url = test_url,
            proxy = proxy_str,
            headers=HEADERS,
            timeout=8,
            ssl=False
        ) as response:
            if response.status == 200:
                proxy_pool.add_proxy(proxy)
    except Exception as e:
        pass

async def batch_verify_proxy(proxies,test_url,proxy_pool):
    async with aiohttp.ClientSession() as session:
        tasks = [
            verify_single_proxy(session, proxy, test_url, proxy_pool)
            for proxy in proxies
        ]
        await asyncio.gather(*tasks)

def main():
    proxy_pool = MemoryProxyPool()
    proxy_pool.clear_proxy()

    raw_proxies = crawl_free_proxy(TEST_URL)
    if not raw_proxies:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] proxy failed")
        return

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]proxy added: {len(raw_proxies)}")
    asyncio.run(batch_verify_proxy(raw_proxies,TEST_URL,proxy_pool))

    total = proxy_pool.proxies_count()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] success")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] useful proxy: {total}")

    random_proxy = proxy_pool.random_proxy()
    if random_proxy:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] random proxy: {random_proxy}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] no random proxy")
if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()
    input("\n enter out")
  feat: 完成内存版代理池核心功能
