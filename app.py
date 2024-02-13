
import asyncio
import sys

from crawler.crawler_cli import CrawlerCLI


def main():
    crawler_cli = CrawlerCLI()
    loop = asyncio.get_event_loop_policy().get_event_loop()
    while True:
        user_input = input('Please enter a url and the desired depth (type "exit" to quit):')
        if user_input.lower() == 'exit':
            break
        input_text = user_input.split(' ')
        loop.run_until_complete(crawler_cli.run(input_text[0], input_text[1]))
    loop.close()

if __name__ == '__main__':
    main()
