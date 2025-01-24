import streamlit as st
from supabase import create_client, Client
from scrapper import scrap_products
from postgres_helper import (
    get_connection, insert_products, fetch_data_by_shopify_url,
    insert_rephrased_product, create_tables_if_not_exist
)
from bs4 import BeautifulSoup
from shopify_api import scrape_single_product
import requests
import pandas as pd
from openai import OpenAI  # Updated import for OpenAI client
import os  # For environment variable

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Shopify API Configuration
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

# OpenAI API Configuration
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_html(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text()

def push_to_shopify(title, description, price, image):
    """Push product data directly to Shopify."""
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN, "Content-Type": "application/json"}
    payload = {
        "product": {
            "title": title,
            "body_html": description,
            "variants": [{"price": float(price)}],
            "images": [{"src": image}] if image else []
        }
    }
    try:
        response = requests.post(
            f"{SHOPIFY_STORE_URL}/admin/api/2024-01/products.json", headers=headers, json=payload
        )
        if response.status_code == 201:
            st.success(f"Product '{title}' pushed to Shopify successfully.")
        else:
            st.error(f"Failed to push product: {response.content}")
    except Exception as e:
        st.error(f"Error pushing product to Shopify: {e}")
def rephrase_text(title, description):
    try:
        # Send request to OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for rephrasing product details. Rephrase the title and description independently, keeping them concise and professional."},
                {"role": "user", "content": f"Title: {title}\nDescription: {description}\nPlease rephrase them separately and return in this exact format:\nTitle: [Rephrased Title]\nDescription: [Rephrased Description]"}
            ]
        )

        # Get the response content
        content = response.choices[0].message.content.strip()

        # Log the raw response for debugging
        st.write("Raw Response from OpenAI:", content)

        # Parse the response
        if "Title:" in content and "Description:" in content:
            # Split the response into lines and parse `Title` and `Description`
            lines = content.split("\n", 1)  # Split into max 2 parts
            rephrased_title = lines[0].replace("Title: ", "").strip()
            rephrased_description = lines[1].replace("Description: ", "").strip()
        else:
            st.error("The response format is incorrect. Using the original title and description.")
            return title, description

        # Ensure both title and description are parsed
        if not rephrased_title:
            st.error("Rephrased title is missing. Using the original title.")
            rephrased_title = title
        if not rephrased_description:
            st.error("Rephrased description is missing. Using the original description.")
            rephrased_description = description

        return rephrased_title, rephrased_description

    except Exception as e:
        st.error(f"Error during rephrasing: {e}")
        return title, description  # Return original if rephrasing fails

def get_product_id(conn, url):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM products WHERE url = %s", (url,))
        result = cursor.fetchone()
        return result[0] if result else None

def fetch_shopify_urls_by_user(conn, user_id):
    """Fetch all Shopify URLs for a specific user."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT DISTINCT shopify_url FROM products WHERE user_id = %s;", (user_id,))
        return [row[0] for row in cursor.fetchall()]

def fetch_user_data_by_url(conn, shopify_url, user_id):
    """Fetch products for a specific Shopify URL and user."""
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM products WHERE shopify_url = %s AND user_id = %s;", 
            (shopify_url, user_id)
        )
        return cursor.fetchall()

def main():
    st.set_page_config(layout="wide")
    st.title("Shopify Product Scraper & Viewer")

    # Initialize Database Tables
    conn = get_connection()
    create_tables_if_not_exist(conn)

    # User Authentication
    if 'user' not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        with st.sidebar:
            st.header("Authentication")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign Up"):
                try:
                    response = supabase.auth.sign_up({"email": email, "password": password})
                    if response.user:
                        st.success("Account created successfully! Please log in.")
                except Exception as e:
                    st.error(f"Error: {e}")

            if st.button("Login"):
                try:
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if response.user:
                        st.session_state.user = response.user.user_metadata
                        st.success("Logged in successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        user_metadata = st.session_state.user
        user_email = user_metadata.get("email", "Unknown")
        user_id = user_metadata.get("sub")  # Unique user ID
        st.sidebar.write(f"Logged in as: **{user_email}**")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()

        st.write("## Scrape All Products from a Shopify Store with Rephrasing")
        store_url = st.text_input("Enter a Shopify store URL (e.g., https://example.myshopify.com):")
        if st.button("Scrape, Rephrase, and Push All Products"):
            if store_url:
                scraped_products = scrap_products(store_url)
                for product in scraped_products:
                    product["user_id"] = user_id
                    product["description"] = clean_html(product.get("description", ""))
                    rephrased_title, rephrased_description = rephrase_text(product.get("title", ""), product.get("description", ""))
                    insert_products(conn, [product], user_id)
                    product_id = get_product_id(conn, product.get("url"))
                    insert_rephrased_product(conn, product_id, rephrased_title, rephrased_description, user_id)
                st.success("All rephrased products pushed and stored successfully!")
            else:
                st.warning("Please enter a valid store URL.")

        st.write("## View Your Products")
        shopify_urls = fetch_shopify_urls_by_user(conn, user_id)

        if shopify_urls:
            for shopify_url in shopify_urls:
                if st.button(f"View Products for {shopify_url}"):
                    products = fetch_user_data_by_url(conn, shopify_url, user_id)
                    if products:
                        st.write(f"### Products for {shopify_url}")
                        df = pd.DataFrame(products)
                        st.table(df)
                    else:
                        st.warning(f"No products found for {shopify_url}.")
        else:
            st.info("No Shopify URLs found for your account.")

        st.write("## Scrape and Push a Single Product with Rephrasing")
        single_product_url = st.text_input("Enter a single product URL (e.g., https://example.myshopify.com/products/product-handle):")

        if st.button("Fetch, Rephrase, and Push Product"):
            if single_product_url:
                product_info = scrape_single_product(single_product_url)
                if product_info:
                    product_info["description"] = clean_html(product_info.get("description", ""))
                    rephrased_title, rephrased_description = rephrase_text(product_info.get("title", ""), product_info.get("description", ""))
                    product_info["user_id"] = user_id
                    insert_products(conn, [product_info], user_id)
                    product_id = get_product_id(conn, product_info.get("url"))
                    insert_rephrased_product(conn, product_id, rephrased_title, rephrased_description, user_id)

                    push_to_shopify(
                        title=rephrased_title,
                        description=rephrased_description,
                        price=product_info.get("price", 0),
                        image=product_info.get("image")
                    )
                    st.success("Rephrased product pushed and stored successfully!")
                else:
                    st.error("Failed to fetch product details. Please check the URL.")
            else:
                st.warning("Please enter a valid product URL.")

if __name__ == "__main__":
    main()
