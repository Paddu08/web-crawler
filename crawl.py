from urllib.parse import urlparse
from bs4 import BeautifulSoup
soup=BeautifulSoup()
def normalize_url(url):
    val=urlparse(url)
    res=val.netloc+val.path
    
    
    return res

def get_h1_from_html(url):
    val =soup.find("h1").get_text()
    print(val)
    return val

def get_first_paragraph_from_html(url):
    pass



    
    
      