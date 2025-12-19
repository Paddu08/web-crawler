from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio


def normalize_url(url):
    val = urlparse(url)
    
    if val.path == "/":
        res = val.netloc
    else:
        res = val.netloc + val.path

    return res

def get_h1_from_html(url):
    soup=BeautifulSoup(url,features="html.parser")
    val =soup.find("h1")
    res=None
    if val is None:
        return ""
    else:
        res=val.get_text()
        

    
    
    return res

def get_first_paragraph_from_html(url):
    soup=BeautifulSoup(url,features="html.parser")
    res=None

    if soup.main is None:

        res=soup.find("p")
        if res is None:
            return ""
        else:
            return res.get_text()
    else:
        res=soup.main.find("p").get_text()
    

    
    
    
    return res


def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, features="html.parser")
    links = []
    for a in soup.find_all('a'):
        href = a.get("href")
        if href:
            full = urljoin(base_url, href)
            links.append(full)
    return links
    
        
def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, features="html.parser")
    images = []
    for img in soup.find_all('img'):
        src = img.get("src")
        if src:
            fulsrc = urljoin(base_url, src)
            images.append(fulsrc)

    return images

def extract_page_data(html, page_url):
    # Build a dict of information about the page using existing helpers
    h1 = get_h1_from_html(html)
    first_paragraph = get_first_paragraph_from_html(html)
    outgoing_links = get_urls_from_html(html, page_url)
    image_urls = get_images_from_html(html, page_url)

    return {
        "page_url": page_url,
        "h1": h1,
        "first_paragraph": first_paragraph,
        "outgoing_link_urls": outgoing_links,
        "image_urls":image_urls,
    }


def get_html(url):
    """Fetch the HTML for `url` using requests and return the HTML string.

    Raises requests.RequestException (including HTTPError) on failure.
    """
    headers = {"User-Agent": "BootCrawler/1.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text


def crawl(base_url, current_url, page_data):
    """Recursively crawl pages under the same domain starting from current_url.

    - Only crawls pages on the same domain as base_url.
    - Uses normalized URL as keys in page_data to avoid revisits.
    - Fetches HTML with get_html and extracts page data with extract_page_data.
    """
    base_netloc = urlparse(base_url).netloc
    cur_netloc = urlparse(current_url).netloc

    # Skip external domains
    if base_netloc != cur_netloc:
        return

    normalized = normalize_url(current_url)
    # Skip already-crawled pages
    if normalized in page_data:
        return

    try:
        html = get_html(current_url)
    except requests.RequestException:
        # On fetch errors, just skip this URL
        return

    # Print current URL so we can watch the crawler in real time
    print(f"Crawling: {current_url}")

    # Extract and store the page data
    data = extract_page_data(html, current_url)
    page_data[normalized] = data

    # Find links and recurse
    for url in get_urls_from_html(html, current_url):
        crawl(base_url, url, page_data)

    


class AsyncCrawler:
    def __init__(self,base_url,max_concurrency,max_pages):

        self.page_data={}
        
        self.should_stop=False
        self.all_tasks= set()

        self.max_pages = max_pages
        self.base_url=base_url
        self.base_domain=urlparse(base_url).netloc
        self.max_concurrency=max_concurrency
        self.lock=asyncio.Lock()
        self.semaphore=asyncio.Semaphore(max_concurrency)
        self.session=None
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    async def add_page_visit(self,normalized_url):
        async with self.lock:
            if self.should_stop:
                return False
            if normalized_url in self.page_data:
                return False
            else:
                
                if len(self.page_data)>=self.max_pages:
                    
                    self.should_stop=True
                    for task in self.all_tasks:
                        task.cancel()
                    return False
                
                self.page_data[normalized_url]=None
                return True
    async def get_html(self,url):
        headers = {"User-Agent": "BootCrawler/1.0"}
        async with self.session.get(url,headers=headers,raise_for_status=True,timeout=aiohttp.ClientTimeout(total=10)) as response:
            return await response.text() 
    async def crawl_page(self,url):
        if self.should_stop:
            return
        
        
        normalized_url=normalize_url(url)
        curr_netloc=urlparse(url).netloc
        if self.base_domain!=curr_netloc:
            return 

        visited=await self.add_page_visit(normalized_url)
        
        
        
        if not visited:
            return
        else:
            async with self.semaphore:
                try:
                    html=await self.get_html(url)
                    
                except aiohttp.ClientError:
                    return
                print(f"Crawling: {url}")
                
                
                async with self.lock:
                    self.page_data[normalized_url]=extract_page_data(html,url)
                urls=get_urls_from_html(html,url)
                tasks=[]
                for url in urls:
                    task = asyncio.create_task(self.crawl_page(url))
                    tasks.append(task)
                    self.all_tasks.add(task)
                if tasks:
                    try:

                        await asyncio.gather(*tasks, return_exceptions=True)
                    finally:
                        for task in tasks:
                            self.all_tasks.discard(task)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data   
async def crawl_site_async(base_url,max_concurrency,max_pages):
    async with AsyncCrawler(base_url,max_concurrency,max_pages) as crawler:    
        result=await crawler.crawl()
        return result
