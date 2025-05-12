from serper import Serper

def find_affiliate_stores(api_key):
    client = Serper(api_key)
    results = client.search("best affiliate programs 2025")
    # Parse "results" buscando nomes, reviews, URLs de afiliação, etc.
    return parsed_stores