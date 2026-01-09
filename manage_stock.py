import sqlite3
import os

def get_db_connection():
    return sqlite3.connect('inventory.db')

def init_db():
    """Ensure tables exist and add 3 starter products with SKUs."""
    conn = get_db_connection()
    c = conn.cursor()
    # Create tables
    c.execute('CREATE TABLE IF NOT EXISTS stock (sku TEXT PRIMARY KEY, name TEXT, quantity INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS logs (sku TEXT, action TEXT, timestamp TEXT)')
    
    # Check if database is empty
    c.execute("SELECT COUNT(*) FROM stock")
    if c.fetchone()[0] == 0:
        print("🌱 Database empty. Adding 3 starter products with SKUs...")
        starter_products = [
            ('SKU-WAT-001', 'Bottled Water', 50),
            ('SKU-CHR-002', 'Office Chair', 12),
            ('SKU-KBD-003', 'Mechanical Keyboard', 25)
        ]
        c.executemany("INSERT INTO stock VALUES (?, ?, ?)", starter_products)
        conn.commit()
        print("✅ Starter items added successfully.")
    
    conn.close()

def add_product(sku, name, initial_qty):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO stock (sku, name, quantity) VALUES (?, ?, ?)", 
                  (sku, name, initial_qty))
        conn.commit()
        print(f"✅ Success: Added {name} (SKU: {sku})")
    except sqlite3.IntegrityError:
        print(f"⚠️ Error: SKU {sku} already exists.")
    finally:
        conn.close()

def view_inventory():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM stock")
    rows = c.fetchall()
    
    print("\n" + "="*50)
    print(f"{'SKU CODE':<15} | {'PRODUCT NAME':<20} | {'QTY':<5}")
    print("-" * 50)
    for row in rows:
        print(f"{row[0]:<15} | {row[1]:<20} | {row[2]:<5}")
    print("="*50 + "\n")
    conn.close()

def menu():
    init_db() 
    while True:
        print("📦 VISILOG INVENTORY MANAGER")
        print("1. Add New Product")
        print("2. View All Stock (and Starter Items)")
        print("3. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            print("\n--- ADD NEW ITEM ---")
            sku = input("Enter SKU (e.g., SKU-ITEM-101): ").upper()
            name = input("Enter Product Name: ")
            try:
                qty = int(input("Initial Stock Level: "))
                add_product(sku, name, qty)
            except ValueError:
                print("❌ Invalid quantity. Please enter a number.")
        elif choice == '2':
            view_inventory()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice, please select 1, 2, or 3.")

if __name__ == "__main__":
    menu()