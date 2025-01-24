from shopify_api import scrape_shopify_products


def scrap_products(url):
    shop_url = url
    products = []
    index = 1
    while True:
        print(f"Fetching Data for Page: {index} ...")
        data = scrape_shopify_products(shop_url, index)
        if not data:
            break
        for product in data:
            product["shopify_url"] = shop_url  # Add shopify_url explicitly
        products.extend(data)
        index += 1

    return products