"""
Setup test data for search and order testing
"""
import os
from supabase import create_client
from openai import OpenAI
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients - use SERVICE_KEY to bypass RLS
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # Service key bypasses RLS
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TEST_USER_ID = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

def get_embedding(text: str):
    """Get embedding from OpenAI"""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def create_test_listings():
    """Create test listings with embeddings"""
    
    test_products = [
        {
            "title": "Brembo Fren Diski Rotor - Ön",
            "description": "Brembo marka yeni ön fren diski. Tüm araçlara uyumlu, yüksek kalite.",
            "price": 2500.00,
            "category": "Otomotiv",
            "location": "İstanbul",
            "condition": "new",
            "stock": 5
        },
        {
            "title": "Performance Rotor Kit - Set",
            "description": "Performans rotoru seti, spor sürüş için ideal. Yüksek ısıya dayanıklı.",
            "price": 4500.00,
            "category": "Otomotiv",
            "location": "Ankara",
            "condition": "new",
            "stock": 3
        },
        {
            "title": "Standart Fren Rotor - Arka",
            "description": "Standart kalite arka fren rotoru. Ekonomik seçenek.",
            "price": 1800.00,
            "category": "Otomotiv",
            "location": "İzmir",
            "condition": "new",
            "stock": 10
        },
        {
            "title": "MacBook Pro 14\" M3 Pro",
            "description": "2024 model MacBook Pro, 16GB RAM, 512GB SSD. Sıfır kutusunda.",
            "price": 85000.00,
            "category": "Elektronik",
            "location": "İstanbul",
            "condition": "new",
            "stock": 2
        },
        {
            "title": "İkinci El Laptop Dell XPS 13",
            "description": "2022 model Dell XPS 13, i7, 16GB RAM. Temiz kullanılmış.",
            "price": 25000.00,
            "category": "Elektronik",
            "location": "İstanbul",
            "condition": "used",
            "stock": 1
        },
        {
            "title": "Gaming Laptop Asus ROG",
            "description": "RTX 4070, i9 işlemci, 32GB RAM. Oyun canavarı.",
            "price": 65000.00,
            "category": "Elektronik",
            "location": "Bursa",
            "condition": "new",
            "stock": 2
        }
    ]
    
    print("Creating test listings...")
    print("=" * 60)
    
    for product in test_products:
        # Create listing - only include columns that exist
        listing_data = {
            "user_id": TEST_USER_ID,
            "title": product["title"],
            "description": product["description"],
            "price": product["price"],
            "category": product["category"],
            "status": "active"
        }
        
        # Add optional fields if they exist in schema
        optional_fields = {
            "location": product.get("location"),
            "condition": product.get("condition"),
            "stock": product.get("stock"),
            "image_url": None
        }
        
        # Only add fields that have values
        for key, value in optional_fields.items():
            if value is not None:
                listing_data[key] = value
        
        try:
            # Insert listing
            result = supabase.table("listings").insert(listing_data).execute()
            listing_id = result.data[0]["id"]
            
            # Generate embedding
            search_text = f"{product['title']} {product['description']} {product['category']}"
            embedding = get_embedding(search_text)
            
            # Insert embedding
            embedding_data = {
                "listing_id": listing_id,
                "embedding": embedding
            }
            supabase.table("product_embeddings").insert(embedding_data).execute()
            
            print(f"✅ {product['title']}")
            print(f"   ID: {listing_id}")
            print(f"   Price: {product['price']} TL")
            print(f"   Category: {product['category']}")
            print()
            
        except Exception as e:
            print(f"❌ Error creating {product['title']}: {e}")
            print()
    
    print("=" * 60)
    print("Test data setup complete!")

def check_existing_data():
    """Check if test data already exists"""
    try:
        result = supabase.table("listings").select("id").eq("user_id", TEST_USER_ID).execute()
        return len(result.data) > 0
    except:
        return False

if __name__ == "__main__":
    print("\nMEGAPAZAR TEST DATA SETUP")
    print("=" * 60)
    
    if check_existing_data():
        print("\n⚠️  Test data already exists!")
        response = input("Delete and recreate? (y/n): ")
        
        if response.lower() == 'y':
            print("\nDeleting existing test data...")
            try:
                # Delete embeddings first (foreign key)
                result = supabase.table("listings").select("id").eq("user_id", TEST_USER_ID).execute()
                listing_ids = [r["id"] for r in result.data]
                
                for lid in listing_ids:
                    supabase.table("product_embeddings").delete().eq("listing_id", lid).execute()
                
                # Delete listings
                supabase.table("listings").delete().eq("user_id", TEST_USER_ID).execute()
                print("✅ Old data deleted")
            except Exception as e:
                print(f"❌ Error deleting: {e}")
        else:
            print("Skipping setup.")
            exit(0)
    
    print("\nCreating new test data...\n")
    create_test_listings()
    
    print("\n✅ Setup complete! You can now run:")
    print("   python test_search_and_order.py")
