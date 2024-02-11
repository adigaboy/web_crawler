# Web Crawler CLI

## About
The tool is designed as a CLI tool which crawls the given URL and calculates the url ratio in the page.
Once a URL crawling process is done a file with the results is created and the program ends.

## System Design
The tool is made up of 2 components:
### WebCrawler
The module is in charge of handling the in page links extraction from the URL and calculating the ratio.
The main logic is written using asyncio Queue to handle all URLs to crawl through.
Main functionality is written in async in order speed up the web page fetches and avoid blocking.

### FileResultGenerator
In charge of writing the results of WebCrawler into a TSV formatted file.

# Technical Details
### Python version
3.11

### Virtual Environment Set Up
``` bash 
python3.11 -m venv <path_to_env>
source <path_to_env>/bin/activate # incase of linux OS
<path_to_env>\Scripts\Activate.ps1 # incase of windows OS

python3.11 -m pip install -r requirements.txt
```

# How To Use
Once virtual environment is set up you can use the tool in the following manner:
python ./app.py <url> <depth>

# How to Test
Run the following command:
``` bash
python3.11 -m pip install -r dev_requirements.txt
```

And after that:
``` bash
pytest crawler\tests --cov-report term-missing --cov=crawler
```

# Author
Nal Zazi
