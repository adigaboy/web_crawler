from typing import List
from crawler.scraped_data_type import ScrapedDataType

results_mock = [
    ["https://www.google.com/", 1, 1.0],
    ["https://www.google.com/intl/iw/policies/privacy/", 2, 1.0],
    ["https://www.google.com/intl/iw/policies/terms/", 2, 1.0],
    ["https://www.google.com/imghp?hl=iw&tab=wi", 2, 1.0],
    ["https://www.google.com/preferences?hl=iw", 2, 1.0],
    ["http://www.google.co.il/intl/iw/services/", 2, 1.0],
    ["https://www.google.com/advanced_search?hl=iw&authuser=0", 3, 1.0],
    ["https://www.google.com/setprefdomain?prefdom=IL&prev=https://www.google.co.il/&sig=K_wAp47ib6jybpcnzUw5LbkWaqp7c%3D", 3, 1.0],
    ["https://www.google.com/intl/iw/about.html", 3, 1.0],
    ["https://www.google.co.il/intl/iw/about/products?tab=wh", 3, 1.0],
    ["https://www.youtube.com/?tab=w1", 3, 1.0],
    ["https://www.google.com/setprefs?sig=0_Q4rVUQGD_nKPh1MIkRI02LcVocs%3D&hl=en&source=homepage&sa=X&ved=0ahUKEwi0pK-0r4yEAxVXQUEAHfncCaQQ2ZgBCAY", 3, 1.0],
    ["https://www.google.com/intl/iw/ads/", 3, 1.0],
    ["https://www.google.com/setprefs?sig=0_Q4rVUQGD_nKPh1MIkRI02LcVocs%3D&hl=ar&source=homepage&sa=X&ved=0ahUKEwi0pK-0r4yEAxVXQUEAHfncCaQQ2ZgBCAU", 3, 1.0],
]

def generate_results() -> List[ScrapedDataType]:
    return [ScrapedDataType(*data) for data in results_mock]
