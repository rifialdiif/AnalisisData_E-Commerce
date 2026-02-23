import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import os

# Konfigurasi halaman
st.set_page_config(page_title="E-Commerce Data Analysis", layout="wide")

# --- DINAMIS PATH UNTUK DEPLOYMENT ---
# Mendapatkan direktori tempat file dashboard.py ini berada
current_dir = os.path.dirname(os.path.abspath(__file__))

# Mendefinisikan path lengkap menuju file CSV
main_data_path = os.path.join(current_dir, "main_data.csv")
geo_data_path = os.path.join(current_dir, "geolocation_dataset.csv")

# --- HELPER FUNCTIONS ---

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date
    recent_date = pd.to_datetime(df["order_purchase_timestamp"]).dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    # Segmentasi berdasarkan ranking
    rfm_df['r_score'] = pd.qcut(rfm_df['recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
    rfm_df['f_score'] = pd.qcut(rfm_df['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm_df['m_score'] = pd.qcut(rfm_df['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    
    def segment_customer(df):
        if df['r_score'] >= 4 and df['f_score'] >= 4: return 'Champions'
        elif df['r_score'] >= 3 and df['f_score'] >= 3: return 'Loyal Customers'
        elif df['r_score'] >= 4 and df['f_score'] <= 2: return 'New Customers'
        elif df['r_score'] <= 2: return 'At Risk / Hibernating'
        else: return 'Others'

    rfm_df['customer_segment'] = rfm_df.apply(segment_customer, axis=1)
    return rfm_df

def create_geospatial_df(df, geolocation_df):
    geo_df = geolocation_df.groupby('geolocation_zip_code_prefix').agg({
        'geolocation_lat': 'mean',
        'geolocation_lng': 'mean'
    }).reset_index()
    
    merged_geo = df.merge(geo_df, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')
    return merged_geo

# --- LOAD DATA ---
try:
    all_df = pd.read_csv(main_data_path)
    all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
except FileNotFoundError:
    st.error(f"Berkas 'main_data.csv' tidak ditemukan di {main_data_path}. Pastikan berkas sudah di-upload ke GitHub.")
    st.stop()

try:
    geo_data = pd.read_csv(geo_data_path)
except FileNotFoundError:
    st.warning(f"Berkas 'geolocation_dataset.csv' tidak ditemukan di {geo_data_path}. Peta tidak akan ditampilkan.")
    geo_data = pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    st.title("E-Commerce Dashboard")
    st.image("https://github.com/rifialdiif/AnalisisData_E-Commerce/blob/main/dashboard/logo.png?raw=true")
    
    min_date = all_df["order_purchase_timestamp"].min()
    max_date = all_df["order_purchase_timestamp"].max()
    
    try:
        start_date, end_date = st.date_input(
            label='Rentang Waktu Analisis',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )
    except ValueError:
        st.error("Pilih rentang tanggal yang valid.")
        start_date, end_date = min_date, max_date

# Filter Data Utama
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# Header Utama
st.title("Public E-Commerce Data Analysis Dashboard")
st.markdown("---")

# --- 1. PRODUCT PERFORMANCE ---
st.header("1. Product Performance Analysis")
product_perf = main_df.groupby("product_category_name_english").agg({
    "price": "sum",
    "review_score": "mean"
}).sort_values(by="price", ascending=False).head(5).reset_index()

# Merapikan nama kategori agar tidak bertabrakan
product_perf["product_category_name_english"] = product_perf["product_category_name_english"].str.replace("_", " ").str.title()

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))

sns.barplot(x="price", y="product_category_name_english", data=product_perf, palette="Blues_r", ax=ax[0])
ax[0].set_title("Top 5 Categories by Revenue", fontsize=20)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Total Revenue (BRL)")
ax[0].tick_params(axis='y', labelsize=14)

sns.barplot(x="review_score", y="product_category_name_english", data=product_perf, palette="Greens_r", ax=ax[1])
ax[1].set_title("Avg Review Score", fontsize=20)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Review Score (0-5)")
ax[1].set_xlim(0, 5)
ax[1].tick_params(axis='y', labelsize=14)

plt.tight_layout()
st.pyplot(fig)
st.info("Insight: Kategori Health & Beauty mendominasi pendapatan dengan tingkat kepuasan yang tinggi.")

# --- 2. GEOGRAPHICS & LOGISTICS ---
st.header("2. Geographics & Logistics Performance")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top States by Customer Count")
    state_df = main_df.groupby("customer_state").customer_id.nunique().sort_values(ascending=False).head(10).reset_index()
    state_df.columns = ['customer_state', 'total_customers']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x="total_customers", y="customer_state", data=state_df, palette="viridis", ax=ax)
    ax.set_xlabel("Number of Unique Customers")
    ax.set_ylabel(None)
    st.pyplot(fig)

with col2:
    st.subheader("Actual vs Estimated Delivery (Days)")
    main_df_copy = main_df.copy()
    main_df_copy['delivery_time'] = (pd.to_datetime(main_df_copy['order_delivered_customer_date']) - main_df_copy['order_purchase_timestamp']).dt.days
    main_df_copy['estimated_time'] = (pd.to_datetime(main_df_copy['order_estimated_delivery_date']) - main_df_copy['order_purchase_timestamp']).dt.days
    
    logistics_df = main_df_copy.groupby("customer_state")[['delivery_time', 'estimated_time']].mean().sort_values(by="delivery_time").head(10).reset_index()
    fig, ax = plt.subplots(figsize=(10, 8))
    logistics_melted = logistics_df.melt(id_vars='customer_state', var_name='Type', value_name='Days')
    sns.barplot(x="Days", y="customer_state", hue="Type", data=logistics_melted, palette="coolwarm")
    ax.set_ylabel(None)
    st.pyplot(fig)
st.info("Insight: Pengiriman di São Paulo (SP) terbukti paling efisien dibandingkan wilayah lainnya.")

# --- 3. GEOSPATIAL MAP ---
st.header("3. Geospatial Distribution Analysis")
if not geo_data.empty:
    geo_map_df = create_geospatial_df(main_df, geo_data)
    fig = px.scatter_mapbox(
        geo_map_df, 
        lat="geolocation_lat", lon="geolocation_lng", 
        color="customer_state", size_max=15, zoom=3, 
        mapbox_style="carto-positron", title="Customer Distribution in Brazil",
        template="plotly_white"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Data geospasial tidak dapat ditampilkan karena berkas tidak ditemukan.")

# --- 4. RFM ANALYSIS ---
st.header("4. Advanced Analysis: RFM Segmentation")
rfm_df = create_rfm_df(main_df)

m1, m2, m3 = st.columns(3)
with m1: st.metric("Avg Recency", f"{round(rfm_df.recency.mean(), 1)} Days")
with m2: st.metric("Avg Frequency", f"{round(rfm_df.frequency.mean(), 2)} Orders")
with m3: st.metric("Avg Monetary", f"R$ {round(rfm_df.monetary.mean(), 2)}")

st.subheader("Customer Segmentation Distribution")
fig, ax = plt.subplots(figsize=(12, 6))
segment_counts = rfm_df['customer_segment'].value_counts().sort_values(ascending=True)
segment_counts.plot(kind='barh', color="#72BCD4")
plt.xlabel("Number of Customers")
st.pyplot(fig)
st.info("Insight: Segmen At Risk / Hibernating merupakan kelompok terbesar, memerlukan strategi reaktivasi segera.")

# --- 5. FINANCIAL & SATISFACTION ---
st.header("5. Financial & Satisfaction Overview")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Payment Methods Distribution")
    payment_df = main_df.groupby("payment_type").order_id.nunique().sort_values(ascending=False).reset_index()
    fig, ax = plt.subplots(figsize=(10, 8))
    plt.pie(x=payment_df['order_id'], labels=payment_df['payment_type'], autopct='%1.1f%%', 
            colors=sns.color_palette("pastel"), wedgeprops={'width': 0.4})
    st.pyplot(fig)

with col2:
    st.subheader("Review Score Distribution")
    review_df = main_df['review_score'].value_counts().sort_index().reset_index()
    review_df.columns = ['Score', 'Count']
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x="Score", y="Count", data=review_df, palette="RdYlGn")
    plt.xlabel("Review Score (1-5)")
    plt.ylabel("Total Reviews")
    st.pyplot(fig)

st.caption('Copyright (c) Rifialdi Faturrochman 2026')