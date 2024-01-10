# Web Crawler CLI

## About
The tool is design as a CLI tool which crawls the given URL and calculates the url ratio in the page.
Once a URL crawling process is done a file with the results is created and the program ends.

## System Design
The tool is made up of 3 components:
# WebCrawler
The module is in charge of handling the in page links extraction from the URL.
The main logic is written in recursion(OMG) and recursion depth is dependent on the wanted depth.
Main functionality is written in async in order speed up the web page fetches as much as possible.

# RatioCalculator
This module is in charge of calculating the URL ratio.

# FileResultGenerator
In charge of writing the results of WebCrawler combined with RatioCalculator into a TSV formatted file.

All components use the LocalCache module.

Other components:
# LocalCache
This module is in charge of managing the cache of the tool in a key value database.

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

# Author
Nal Zazi
