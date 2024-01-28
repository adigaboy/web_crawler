from urllib.parse import urlparse


def get_url_domain(url: str) -> str:
    return urlparse(url).netloc

def get_url_scheme(url: str) -> str:
    return urlparse(url).scheme
