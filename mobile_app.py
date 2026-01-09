import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- MOBILE CONFIG ---
st.set_page_config(page_title="Visilog Mobile Admin", layout="centered")

def get_db_connection():
    return sqlite3.connect('inventory.db')

# Custom CSS for Mobile Styling
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #ddd; }
    .main { background-color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FETCH ---
conn = get_db_connection()
df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
df_logs = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10", conn)
conn.close()

# --- HEADER ---
st.title("📱 Admin Mobile")
st.write(f"Updated: {datetime.now().strftime('%H:%M')}")

# --- 1. QUICK STATUS (Cards) ---
st.subheader("System Status")
low_stock_count = len(df_stock[df_stock['quantity'] < 10])

c1, c2 = st.columns(2)
with c1:
    st.metric("📦 Items", len(df_stock))
with c2:
    status_color = "🔴" if low_stock_count > 0 else "🟢"
    st.metric("Alerts", f"{status_color} {low_stock_count}")

# --- 2. CRITICAL ALERTS ---
if low_stock_count > 0:
    with st.expander("🚨 CRITICAL LOW STOCK", expanded=True):
        low_items = df_stock[df_stock['quantity'] < 10]
        for _, item in low_items.iterrows():
            st.warning(f"**{item['name']}**: {item['quantity']} left")

# --- 3. RECENT ACTIVITY (Simple List) ---
st.subheader("🕒 Recent Activity")
for _, log in df_logs.head(5).iterrows():
    # Find name for the SKU
    p_name = df_stock[df_stock['sku'] == log['sku']]['name'].iloc[0] if log['sku'] in df_stock['sku'].values else "Unknown"
    icon = "📥" if log['action'] == "IN" else "📤"
    st.info(f"{icon} **{p_name}** | {log['action']} at {log['timestamp']}")

# --- 4. QUICK SEARCH ---
st.divider()
st.subheader("🔍 Find Product")
search_query = st.text_input("Enter SKU or Name")
if search_query:
    results = df_stock[df_stock['name'].str.contains(search_query, case=False) | df_stock['sku'].str.contains(search_query, case=False)]
    if not results.empty:
        for _, res in results.iterrows():
            st.success(f"**{res['name']}**\n\nSKU: {res['sku']} | Stock: {res['quantity']}")
    else:
        st.error("No item found.")

# --- FOOTER ---
if st.button("🔄 Refresh Data"):
    st.rerun()