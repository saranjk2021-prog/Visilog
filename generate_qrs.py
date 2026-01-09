import qrcode
import sqlite3
import os

def generate_product_qrs():
    # 1. Create a folder to save images
    if not os.path.exists('product_qrs'):
        os.makedirs('product_qrs')
        print("📁 Created folder: product_qrs")

    # 2. Connect to database
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT sku, name FROM stock")
    products = c.fetchall()
    
    if not products:
        print("❌ No products found in database. Add some using manage_stock.py first!")
        return

    # 3. Generate QR for each product
    for sku, name in products:
        # Create the QR object
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(sku)
        qr.make(fit=True)

        # Create image and save
        img = qr.make_image(fill_color="black", back_color="white")
        filename = f"product_qrs/{name.replace(' ', '_')}_QR.png"
        img.save(filename)
        print(f"✅ Generated: {filename} (SKU: {sku})")

    conn.close()
    print("\n🚀 All QR codes generated! You can find them in the 'product_qrs' folder.")

if __name__ == "__main__":
    generate_product_qrs()