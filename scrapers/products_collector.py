import requests

def collect_products_for_store(store, serper_mcp_url):
    resp = requests.get(f"{serper_mcp_url}/products", params={"store": store['platform']})
    return resp.json()