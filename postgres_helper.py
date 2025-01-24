import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_connection():
    """Establish connection to PostgreSQL database."""
    conn = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME")
    )
    return conn

def create_tables_if_not_exist(conn):
    """Create necessary tables if they don't exist."""
    create_scraped_urls_table = """
    CREATE TABLE IF NOT EXISTS scraped_urls (
        id SERIAL PRIMARY KEY,
        shopify_url TEXT UNIQUE NOT NULL,
        user_id UUID NOT NULL
    );
    """
    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price NUMERIC NOT NULL,
        image TEXT,
        url TEXT UNIQUE NOT NULL,
        shopify_url TEXT NOT NULL REFERENCES scraped_urls(shopify_url),
        user_id UUID NOT NULL
    );
    """
    create_rephrased_products_table = """
    CREATE TABLE IF NOT EXISTS rephrased_products (
        id SERIAL PRIMARY KEY,
        original_product_id INT NOT NULL REFERENCES products(id),
        rephrased_title TEXT NOT NULL,
        rephrased_description TEXT NOT NULL,
        user_id UUID NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with conn.cursor() as cursor:
        cursor.execute(create_scraped_urls_table)
        cursor.execute(create_products_table)
        cursor.execute(create_rephrased_products_table)
        conn.commit()

def insert_products(conn, products, user_id):
    """Insert scraped products into the PostgreSQL table."""
    with conn.cursor() as cursor:
        for product in products:
            cursor.execute(
                """
                INSERT INTO products (title, description, price, image, url, shopify_url, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (
                    product["title"],
                    product["description"],
                    product["price"],
                    product["image"],
                    product["url"],
                    product["shopify_url"],
                    user_id,
                ),
            )
        conn.commit()

def insert_rephrased_product(conn, original_product_id, rephrased_title, rephrased_description, user_id):
    """Insert rephrased product data into the rephrased_products table."""
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO rephrased_products (original_product_id, rephrased_title, rephrased_description, user_id)
            VALUES (%s, %s, %s, %s);
            """,
            (original_product_id, rephrased_title, rephrased_description, user_id)
        )
        conn.commit()


def fetch_data_by_shopify_url(conn, shopify_url):
    """Fetch products for a specific Shopify URL."""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM products WHERE shopify_url = %s;", (shopify_url,))
        return cursor.fetchall()
def fetch_shopify_urls_by_user(conn, user_id):
    """Fetch all Shopify URLs for a specific user."""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT shopify_url FROM scraped_urls WHERE user_id = %s;", (user_id,)
        )
        return cursor.fetchall()
def fetch_user_data_by_url(conn, shopify_url, user_id):
    """Fetch products for a specific Shopify URL and user."""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT * FROM products WHERE shopify_url = %s AND user_id = %s;", 
            (shopify_url, user_id)
        )
        return cursor.fetchall()