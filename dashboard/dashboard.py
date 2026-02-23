import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman
st.set_page_config(page_title="E-Commerce Data Analysis", layout="wide")

# Fungsi untuk menyiapkan data RFM
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
    
    # Segmentasi
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

# Load Data
all_df = pd.read_csv("main_data.csv")
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

# --- SIDEBAR ---
with st.sidebar:
    st.title("RF Dashboard 📊")
    st.image("https://png.pngtree.com/png-clipart/20220403/ourmid/pngtree-e-commerce-shopping-business-icon-png-image_4525684.png")
    
    # Filter Rentang Waktu
    min_date = all_df["order_purchase_timestamp"].min()
    max_date = all_df["order_purchase_timestamp"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu Analisis',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter Data
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

# Header Utama
st.title("Public E-Commerce Data Analysis Dashboard")
st.markdown("---")

# --- PERTANYAAN 1: PRODUK ---
st.header("1. Product Performance Analysis")
st.subheader("Revenue vs Customer Satisfaction")

# Agregasi Pertanyaan 1
product_perf = main_df.groupby("product_category_name_english").agg({
    "price": "sum",
    "review_score": "mean"
}).sort_values(by="price", ascending=False).head(5).reset_index()

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 8))
sns.barplot(x="price", y="product_category_name_english", data=product_perf, palette="Blues_r", ax=ax[0])
ax[0].set_title("Top 5 Categories by Revenue", fontsize=15)

sns.barplot(x="review_score", y="product_category_name_english", data=product_perf, palette="Greens_r", ax=ax[1])
ax[1].set_title("Avg Review Score for Top Categories", fontsize=15)
ax[1].set_xlim(0, 5)

st.pyplot(fig)
st.info("Insight: Health & Beauty mendominasi pendapatan, namun perhatikan skor ulasan pada kategori dengan pendapatan tinggi lainnya.")

# --- PERTANYAAN 2: GEOGRAFIS & LOGISTIK ---
st.header("2. Geographics & Logistics Performance")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top States by Customer Count")
    state_df = main_df.groupby("customer_state").customer_id.nunique().sort_values(ascending=False).head(10).reset_index()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x="customer_id", y="customer_state", data=state_df, palette="viridis")
    st.pyplot(fig)

with col2:
    st.subheader("Actual vs Estimated Delivery (Days)")
    main_df['delivery_time'] = (pd.to_datetime(main_df['order_delivered_customer_date']) - main_df['order_purchase_timestamp']).dt.days
    main_df['estimated_time'] = (pd.to_datetime(main_df['order_estimated_delivery_date']) - main_df['order_purchase_timestamp']).dt.days
    
    logistics_df = main_df.groupby("customer_state")[['delivery_time', 'estimated_time']].mean().sort_values(by="delivery_time").head(10).reset_index()
    fig, ax = plt.subplots(figsize=(10, 8))
    logistics_melted = logistics_df.melt(id_vars='customer_state', var_name='Type', value_name='Days')
    sns.barplot(x="Days", y="customer_state", hue="Type", data=logistics_melted, palette="coolwarm")
    st.pyplot(fig)

# --- ANALISIS LANJUTAN: RFM ---
st.header("3. Advanced Analysis: RFM Segmentation")
rfm_df = create_rfm_df(main_df)

# Metrics RFM
m1, m2, m3 = st.columns(3)
with m1: st.metric("Avg Recency", f"{round(rfm_df.recency.mean(), 1)} Days")
with m2: st.metric("Avg Frequency", f"{round(rfm_df.frequency.mean(), 2)} Orders")
with m3: st.metric("Avg Monetary", f"R$ {round(rfm_df.monetary.mean(), 2)}")

# Plot Segmentasi
st.subheader("Customer Segmentation Distribution")
fig, ax = plt.subplots(figsize=(12, 6))
segment_counts = rfm_df['customer_segment'].value_counts().sort_values(ascending=True)
segment_counts.plot(kind='barh', color="#72BCD4")
plt.xlabel("Number of Customers")
st.pyplot(fig)

st.caption('Copyright (c) Rifialdi Faturrochman 2026')