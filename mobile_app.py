import streamlit as st
import sqlite3
import pandas as pd

# --- MOBILE APP THEME ---
st.set_page_config(page_title="Visilog Mobile", layout="centered")

def run_query(query, params=()):
    with sqlite3.connect('inventory.db') as conn:
        return pd.read_sql_query(query, conn) if "SELECT" in query else conn.execute(query, params)

st.title("📦 Visilog Mobile")

# --- 1. QUICK ACTIONS ---
with st.expander("➕ Add New Transaction", expanded=False):
    sku_list = run_query("SELECT sku FROM stock")['sku'].tolist()
    selected_sku = st.selectbox("Select SKU", sku_list)
    action_type = st.radio("Action", ["IN", "OUT"], horizontal=True)
    
    if st.button("Confirm Transaction"):
        delta = 1 if action_type == "IN" else -1
        # Update Stock
        with sqlite3.connect('inventory.db') as conn:
            conn.execute("UPDATE stock SET quantity = quantity + ? WHERE sku = ?", (delta, selected_sku))
            conn.execute("INSERT INTO logs (sku, action, timestamp) VALUES (?, ?, datetime('now'))", (selected_sku, action_type))
        st.success(f"Updated {selected_sku}!")
        st.rerun()

# --- 2. THE INVENTORY LIST ---
st.subheader("Current Stock")
df = run_query("SELECT name, quantity, sku FROM stock")

for _, row in df.iterrows():
    # Create a nice card for each item
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{row['name']}**")
            st.caption(f"SKU: {row['sku']}")
        with col2:
            color = "red" if row['quantity'] < 10 else "green"
            st.markdown(f"<h3 style='text-align:right;color:{color};'>{row['quantity']}</h3>", unsafe_allow_html=True)
        st.divider()

import streamlit as st
from supabase import create_client

# Use the secrets we added to Streamlit Cloud
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Correct way to fetch data from Supabase
def get_data():
    # This calls the 'stock' table we just created in the SQL Editor
    response = supabase.table("stock").select("*").execute()
    return response.data