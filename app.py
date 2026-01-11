import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Setup Supabase Connection using Streamlit Secrets
# Make sure you added these in Advanced Settings!
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Missing Supabase Secrets! Go to Advanced Settings and add SUPABASE_URL and SUPABASE_KEY.")
    st.stop()

st.set_page_config(page_title="Visilog Inventory Dashboard", layout="wide")

st.title("📦 Visilog: Real-Time Inventory Dashboard")

# 2. Function to fetch data from Supabase
def fetch_inventory():
    try:
        # This calls the 'stock' table you created in the SQL Editor
        response = supabase.table("stock").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

# 3. Load and Display Data
df = fetch_inventory()

if not df.empty:
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(df))
    with col2:
        st.metric("Total Stock Quantity", df['quantity'].sum())
    with col3:
        st.metric("Categories", df['category'].nunique())

    # Main Table
    st.subheader("Current Stock Levels")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No data found in the 'stock' table. Please ensure you ran the SQL script in Supabase.")

# 4. Auto-refresh button
if st.button('🔄 Refresh Data'):
    st.rerun()