import requests


def scrape_shopify_products(shop_url, page=1):
    """Scrapes products from a Shopify store using the public products.json API"""
    product_api_url = f"{shop_url}/products.json?page={page}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(product_api_url, headers=headers, verify=False)
        response.raise_for_status()
        product_data = response.json()

        # Extract product information
        products = []
        for product in product_data['products']:
            product_info = {
                'title': product['title'],
                'price': product['variants'][0]['price'],
                'description': product['body_html'],
                'image': product['images'][0]['src'] if product['images'] else None,
                'url': f"{shop_url}/products/{product['handle']}"
            }
            products.append(product_info)

        return products

    except requests.exceptions.RequestException as e:
        print(f"Error fetching products: {e}")
        return []
def scrape_single_product(product_url):
    """
    Scrapes a single product from a Shopify product URL using the public JSON API.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Extract product handle from the URL
        if "/products/" in product_url:
            handle = product_url.split("/products/")[-1].split("/")[0]
        else:
            print("Invalid product URL")
            return None

        # Build API URL
        base_url = '/'.join(product_url.split('/')[:3])
        product_api_url = f"{base_url}/products/{handle}.json"

        # Fetch product data
        response = requests.get(product_api_url, headers=headers)
        response.raise_for_status()
        product_data = response.json()

        # Extract product details
        product = product_data.get('product', {})
        product_info = {
            "title": product.get('title'),
            "description": product.get('body_html'),
            "price": product.get('variants', [{}])[0].get('price'),
            "image": product.get('images', [{}])[0].get('src'),
            "url": product_url,
            "shopify_url": base_url  # Include the base Shopify URL
        }
        return product_info
    except Exception as e:
        print(f"Error fetching product: {e}")
        return None

# Testing
# shop_url = "https://two18.com/"
# products = []
# index = 1
# while (True):
#     print(f"Fetching Data for Page: {index} ...")
#     data = scrape_shopify_products(shop_url, index)
#     if not data:
#         break
#     products.extend(data)
#     index += 1

# print(products)
