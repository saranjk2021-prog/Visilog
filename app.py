import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Visilog AI Dashboard", layout="wide")

def get_data(query):
    conn = sqlite3.connect('inventory.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- HEADER ---
st.title("🚀 Visilog AI Inventory Dashboard")
st.markdown("Real-time monitoring of AI-scanned inventory and hand-gesture logs.")

# --- SIDEBAR / REFRESH ---
if st.sidebar.button('🔄 Refresh Data'):
    st.rerun()

# --- 1. KEY METRICS ---
df_stock = get_data("SELECT * FROM stock")
df_logs = get_data("SELECT * FROM logs")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Products", len(df_stock))
with col2:
    total_qty = df_stock['quantity'].sum()
    st.metric("Total Units in Stock", int(total_qty))
with col3:
    ins = len(df_logs[df_logs['action'] == 'IN'])
    st.metric("Total Scanned IN", ins)
with col4:
    outs = len(df_logs[df_logs['action'] == 'OUT'])
    st.metric("Total Scanned OUT", outs)

st.divider()

# --- 2. VISUALIZATIONS ---
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📦 Stock Levels by Product")
    fig_stock = px.bar(df_stock, x='name', y='quantity', 
                       color='quantity', color_continuous_scale='Viridis',
                       labels={'name': 'Product', 'quantity': 'Quantity'})
    st.plotly_chart(fig_stock, use_container_width=True)

with right_col:
    st.subheader("🕒 Recent Activity Trend")
    # Group logs by hour or just show last 10
    if not df_logs.empty:
        df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
        # Simple count of actions
        fig_logs = px.pie(df_logs, names='action', title="Activity Split (IN vs OUT)",
                          color='action', color_discrete_map={'IN':'#00CC96', 'OUT':'#EF553B'})
        st.plotly_chart(fig_logs, use_container_width=True)
    else:
        st.info("No logs available yet.")

# --- 3. DATA TABLES ---
st.divider()
tab1, tab2 = st.tabs(["📋 Current Inventory", "📜 Transaction Logs"])

with tab1:
    # Highlight low stock
    def color_low_stock(val):
        color = 'red' if val < 10 else 'white'
        return f'color: {color}'
    
    st.dataframe(df_stock.style.applymap(color_low_stock, subset=['quantity']), use_container_width=True)

with tab2:
    if not df_logs.empty:
        # Join logs with stock to get names
        df_full_logs = df_logs.merge(df_stock[['sku', 'name']], on='sku', how='left')
        st.dataframe(df_full_logs.sort_values(by='timestamp', ascending=False), use_container_width=True)
    else:
        st.write("No transactions recorded.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.write(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")