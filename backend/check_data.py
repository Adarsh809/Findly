from sqlmodel import Session, select
from backend.database import engine
from models import Product

def view_data():
    with Session(engine) as session:
        # Get all products
        products = session.exec(select(Product)).all()
        
        print(f"\n📊 Total Products found: {len(products)}\n")
        print("-" * 80)
        print(f"{'ID':<5} | {'Title':<40} | {'Price':<15}")
        print("-" * 80)
        
        for p in products:
            # Truncate title if it's too long so it fits in the table
            short_title = (p.title[:37] + '...') if len(p.title) > 37 else p.title
            print(f"{p.id:<5} | {short_title:<40} | {p.price:<15}")

if __name__ == "__main__":
    view_data()