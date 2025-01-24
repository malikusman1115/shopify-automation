<!-- mike_listing_bot -->
# Shopify Content Scraper

A Python-based web scraping tool that scrapes product details from Shopify stores, rephrases product descriptions using OpenAI, and optionally pushes them back to the Shopify store via API.

---

## Features

- Scrape all products from a Shopify store using the public `products.json` API.
- Rephrase product descriptions using OpenAI's GPT API.
- Store product data in a PostgreSQL database.
- Push rephrased products back to the Shopify store.
- User authentication and account management using Supabase.

---

## Prerequisites

- Python 3.8+
- PostgreSQL
- Supabase account
- Shopify Admin API access token
- OpenAI API key

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd shopify-content-scraper
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root and add the following:
   ```env
   SUPABASE_URL=<Your Supabase URL>
   SUPABASE_ANON_KEY=<Your Supabase Anon Key>
   SHOPIFY_ACCESS_TOKEN=<Your Shopify Admin API Token>
   SHOPIFY_STORE_URL=<Your Shopify Store URL>
   OPENAI_API_KEY=<Your OpenAI API Key>
   DB_USER=<PostgreSQL Username>
   DB_PASSWORD=<PostgreSQL Password>
   DB_HOST=<PostgreSQL Host>
   DB_PORT=<PostgreSQL Port>
   DB_NAME=<PostgreSQL Database Name>
   ```

---

## Usage

### Run the Application
```bash
streamlit run app.py
```

### Features in the App
1. **Scrape Products**
   - Enter a Shopify store URL to scrape all products.
   - The app will fetch, rephrase, and optionally push products to the Shopify store.

2. **View Products**
   - View previously scraped products from your account stored in the PostgreSQL database.

3. **Scrape a Single Product**
   - Enter a specific product URL to fetch, rephrase, and push.

---

## Project Structure

```
.
├── app.py                    # Main application file (Streamlit-based)
├── scrapper.py               # Contains functions to scrape products from Shopify
├── shopify_api.py            # Handles Shopify API interactions
├── postgres_helper.py        # PostgreSQL database operations
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## Database Schema

- **scraped_urls**
  - `id`: Primary key
  - `shopify_url`: Shopify store URL
  - `user_id`: User associated with the URL

- **products**
  - `id`: Primary key
  - `title`, `description`, `price`, `image`, `url`: Product details
  - `shopify_url`: Associated store URL
  - `user_id`: User ID

- **rephrased_products**
  - `id`: Primary key
  - `original_product_id`: References `products` table
  - `rephrased_title`, `rephrased_description`: Rephrased content
  - `user_id`: User ID

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and submit a pull request.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- OpenAI for GPT-powered text rephrasing.
- Shopify for the open `products.json` API.
- Supabase for authentication and user management.
