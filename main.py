from crawl import extract_page_data,AsyncCrawler,crawl_site_async
import sys
import json
import asyncio
from csv_report import write_csv_report




async def main(argv=None):
    argv = sys.argv if argv is None else argv
    if len(argv) < 4:
        print("no website provided")
        return 1
    if len(argv) > 4:
        print("too many arguments provided")
        return 1

    url = argv[1]
    max_concurrency=int(argv[2])
    max_pages=int(argv[3])
    
    print("starting crawl")
    print(url)
    page_data = await crawl_site_async(url,max_concurrency,max_pages)
    write_csv_report(page_data)

   

    # Print the raw HTML (so externa checks can grep for tags like <body)
    # for data in page_data.values():
    #     print(json.dumps(data))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))





            
   
        
        


    
    

        