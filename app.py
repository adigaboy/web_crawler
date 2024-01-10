
import asyncio
import sys

from crawler.crawler_cli import CrawlerCLI


def main():
    crawler_cli = CrawlerCLI()
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(crawler_cli.run(sys.argv[1], sys.argv[2]))
    loop.close()

if __name__ == '__main__':
    main()
