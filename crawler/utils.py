from urllib.parse import urljoin, urlparse


def get_url_domain(url: str) -> str:
    return urlparse(url).netloc

def get_url_scheme(url: str) -> str:
    return urlparse(url).scheme

def fix_url(url: str, main_url: str) -> str:
    scheme = get_url_scheme(url)
    if not scheme:
        url = urljoin(main_url, url)
    elif scheme not in ['https', 'http']:
        return None
    domain = get_url_domain(url)
    if domain == '':
        url = urljoin(main_url, url)
    return url
