import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, select
from backend.database import engine, create_db_and_tables
from models import Product
from backend.utils import get_embedding
import time
import re  # <--- NEW: Import Regex library

# --- CONFIGURATION ---
BASE_URL = "https://traya.health/collections/all-products"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- NEW HELPER FUNCTION ---
def clean_price(price_text):
    """
    Extracts only the currency and number (e.g., '₹ 951') from messy text.
    """
    if not price_text:
        return "N/A"
    
    # This regex looks for: 
    # 1. The Rupee symbol (₹)
    # 2. Optional space (\s?)
    # 3. Digits and commas ([\d,]+)
    match = re.search(r"(₹\s?[\d,]+)", price_text)
    
    if match:
        return match.group(1) # Return just '₹ 951'
    return price_text # Fallback if no match

def scrape_traya():
    print("🚀 Scraper Starting (with Price Cleaning)...")
    create_db_and_tables()

    try:
        response = requests.get(BASE_URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        
        product_cards = soup.select(".product-card, .product-item, .grid__item") 
        
        if not product_cards:
            print("⚠️ No products found! Check CSS selectors.")
            return

        print(f"📦 Found {len(product_cards)} products.")

        with Session(engine) as session:
            count = 0
            for card in product_cards:
                if count >= 30: break 

                try:
                    title_tag = card.find("h3") or card.find(class_="product-title")
                    # We grab the messy text first
                    price_tag = card.find(class_="price") or card.find(class_="money") or card.find(class_="price-item--sale")
                    link_tag = card.find("a")
                    img_tag = card.find("img")

                    if not title_tag or not link_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    
                    # --- CLEAN THE PRICE HERE ---
                    messy_price = price_tag.get_text(strip=True) if price_tag else "N/A"
                    clean_price_val = clean_price(messy_price)

                    relative_link = link_tag['href']
                    product_url = f"https://traya.health{relative_link}" if relative_link.startswith("/") else relative_link
                    
                    image_url = ""
                    if img_tag:
                        src = img_tag.get('src', '') or img_tag.get('data-src', '')
                        image_url = f"https:{src}" if src.startswith("//") else src

                    # Duplicate Check
                    existing = session.exec(select(Product).where(Product.title == title)).first()
                    if existing:
                        print(f"⏩ Skipping {title}")
                        continue

                    print(f"🔍 Processing: {title}")

                    # Details
                    p_resp = requests.get(product_url, headers=HEADERS)
                    p_soup = BeautifulSoup(p_resp.content, "html.parser")
                    
                    description_tag = p_soup.find(class_="product-description") or p_soup.find("div", {"itemprop": "description"})
                    description = description_tag.get_text(strip=True) if description_tag else title

                    # Embedding (using the CLEAN price now)
                    rag_text = f"Product: {title}. Description: {description}. Price: {clean_price_val}"
                    vector = get_embedding(rag_text)

                    if not vector:
                        print(f"⚠️ Embedding failed for {title}")
                        continue

                    new_product = Product(
                        title=title,
                        price=clean_price_val,  # <--- SAVING CLEAN PRICE
                        description=description[:1000],
                        features="Hair Care",
                        image_url=image_url,
                        category="Hair Care",
                        product_url=product_url,
                        embedding=vector
                    )
                    
                    session.add(new_product)
                    session.commit()
                    count += 1
                    print(f"✅ Saved ({count}/30) - Price: {clean_price_val}")
                    time.sleep(1)

                except Exception as e:
                    session.rollback()
                    print(f"❌ Error: {e}")

    except Exception as e:
        print(f"🔥 Critical Error: {e}")

if __name__ == "__main__":
    scrape_traya()