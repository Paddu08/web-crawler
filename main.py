from crawl import extract_page_data
import sys
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def main(argv=None):
    argv = sys.argv if argv is None else argv
    if len(argv) < 2:
        print("no website provided")
        return 1
    if len(argv) > 2:
        print("too many arguments provided")
        return 1

    url = argv[1]
    
    print("starting crawl")
    print(url)
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as e:
        print(f"Error fetching {url}: {e}")
        return 1

    # Print the raw HTML (so externa checks can grep for tags like <body)
    print(html)

    data = extract_page_data(html, url)
    print(json.dumps(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())