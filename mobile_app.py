import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Setup Supabase Connection
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Missing Supabase Secrets in Streamlit Settings!")
    st.stop()

st.title("🛠️ Manage Inventory Database")

# This is what a Dashboard looks like, unlike the Management tool
st.subheader("📊 Live Inventory Dashboard")

# Fetch all data to show on screen
df = pd.DataFrame(supabase.table("stock").select("*").execute().data)

if not df.empty:
    # Shows the visual "Dashboard" tiles
    st.metric("Total Unique SKUs", len(df))
    st.metric("Total Stock Volume", df['quantity'].sum())
    
    # Shows the actual table content
    st.dataframe(df)
# --- SECTION 1: ADD NEW ITEM ---
st.subheader("➕ Add New Product")
with st.form("add_form", clear_on_submit=True):
    new_sku = st.text_input("SKU (Unique ID)")
    new_name = st.text_input("Item Name")
    new_cat = st.selectbox("Category", ["Electronics", "Furniture", "Stationery", "Other"])
    new_qty = st.number_input("Initial Quantity", min_value=0, step=1)
    
    submit = st.form_submit_button("Add to Cloud Database")
    
    if submit:
        if new_sku and new_name:
            try:
                # Insert data into the 'stock' table
                data = {
                    "sku": new_sku, 
                    "item_name": new_name, 
                    "category": new_cat, 
                    "quantity": new_qty
                }
                supabase.table("stock").insert(data).execute()
                st.success(f"✅ {new_name} added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill in SKU and Item Name.")

# --- SECTION 2: DELETE ITEM ---
st.subheader("🗑️ Remove Product")
try:
    # Fetch current SKUs for the dropdown
    res = supabase.table("stock").select("sku").execute()
    sku_list = [item['sku'] for item in res.data]
    
    if sku_list:
        delete_sku = st.selectbox("Select SKU to Delete", sku_list)
        if st.button("Confirm Delete", type="primary"):
            supabase.table("stock").delete().eq("sku", delete_sku).execute()
            st.success(f"Deleted {delete_sku}")
            st.rerun()
    else:
        st.info("No items available to delete.")
except Exception as e:
    st.error(f"Could not load delete list: {e}")


