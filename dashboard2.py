import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')



# Membuat df monthly_orders_df
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='M', on='order_delivered_customer_date').agg({ #rule = M(Monthly), on = pada kolom
        "order_id": "nunique",
        "price": "sum"
        })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
        }, inplace=True)
    return monthly_orders_df

# Membuat df sum_order_items_df
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").product_id.nunique().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# Membuat df customer_bycity_df
def create_customer_bycity_df(df):
    customer_bycity_df = df.groupby("customer_city").customer_id.nunique().sort_values(ascending=False).reset_index().head(5)
    customer_bycity_df.rename(columns={
        "customer_id": "customer_count"
        }, inplace=True)
    return customer_bycity_df

# Membuat df customer_bystate_df
def create_customer_bystate_df(df):
    customer_bystate_df = df.groupby("customer_state").customer_id.nunique().sort_values(ascending=False).reset_index().head(5)
    customer_bystate_df.rename(columns={
        "customer_id": "customer_count"
        }, inplace=True)
    return customer_bystate_df

# Membuat df rfm_df
def create_rfm_df(df):
    rfm_df = df.groupby(by="seller_id", as_index=False).agg({
        "order_id": "nunique", # menghitung jumlah order
        "price": "sum" # menghitung jumlah revenue yang dihasilkan
        })
    rfm_df.columns = ["seller_id", "frequency", "monetary"]
    return rfm_df

# Load berkas all data
all_df = pd.read_csv("https://raw.githubusercontent.com/sabrinalaillita/E-CommerceDicoding/main/all_data.csv")

# Mengubah Tipe Data Menjadi Datetime
datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])

# Filter berdasarkan order_delivered_customer_date dengan widget dateinput pada sidebar
min_date = all_df["order_delivered_customer_date"].min()
max_date = all_df["order_delivered_customer_date"].max()
 

# Membuat layout

# Page config
st.set_page_config(page_title="Sabrina E-Commerce Dashboard",
                   page_icon="https://github.com/sabrinalaillita/E-CommerceDicoding/blob/main/download__4_-removebg-preview.png?raw=true",
                   layout="wide",
                   initial_sidebar_state="expanded"
                   )

with st.sidebar: # Menggunakan sidebar
    # Menambahkan logo perusahaan
    st.image("https://github.com/sabrinalaillita/E-CommerceDicoding/blob/main/download__4_-removebg-preview.png?raw=true")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Input dimasukkan ke main_df
    main_df = all_df[(all_df["order_delivered_customer_date"] >= str(start_date)) & 
                (all_df["order_delivered_customer_date"] <= str(end_date))]
    
# Memanggil semua Dataframe sesuai tanggal
monthly_orders_df = create_monthly_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
customer_bycity_df = create_customer_bycity_df(main_df)
customer_bystate_df = create_customer_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# Membuat Tampilan web

st.header('Sabrina E-Commerce Dashboard :shopping_trolley:')

st.subheader('Monthly Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "USD", locale='en_US')
    st.metric("Total Revenue", value=total_revenue)
    
with st.expander("See Explanataion"):
    st.write(
       """Monthly order is a summary of transactions conducted on a monthly basis.
       The data used encompasses information from 2016 to 2018.
       The chart depicts the quantity of orders received by the company and the company's economic growth."""
    )

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_delivered_customer_date"],
    monthly_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9",
    )
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)
ax.set_title("Number of Orders  per Month (2016-2018)", loc="center", fontsize=30)

st.pyplot(fig)


fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_delivered_customer_date"],
    monthly_orders_df["revenue"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
    )

ax.set_title("Total Revenue per Month (2016-2018)", loc="center", fontsize=30)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15, rotation=45)

st.pyplot(fig)

# Membuat Subheader2 kategori produk terbaik berdasarkan pendapatan
st.subheader("Best & Worst Performing Product Category")

with st.expander("See Explanataion"):
    st.write(
       """The Best & Worst Performing Product Category is a ranking based on the number of orders for each product category.
       The best-performing product category is the one with the highest number of orders,
       while the worst-performing product category is the one with the fewest number of orders."""
    )

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=35)
ax[0].set_title("Best Performing Product Category", loc="center", fontsize=35)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(x="product_id", y="product_category_name", data=sum_order_items_df.sort_values(by="product_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=35)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product Category", loc="center", fontsize=35)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)

# Membuat Subheader3 Seller terbaik
st.subheader("Best Seller")

with st.expander("See Explanataion"):
    st.write(
       """Best Seller is a ranking of sellers based on two categories.
       The first is based on sales, and the second is based on income.
       The sales category is assessed by the number of orders received, while the income category is evaluated by the amount of money received by the seller.
       The results shown are not the name of the seller, but the ID of the seller."""
    )

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot( x="frequency", y="seller_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Based on Sales", loc="center", fontsize=45)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(x="monetary", y="seller_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Based on Income", loc="center", fontsize=45)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

# Membuat Subheader4 Demografi Pelanggan
st.subheader("Customer Demographics")


with st.expander("See Explanataion"):
    st.write(
       """Customer demographics indicate variations among customers. In this analysis, the customer demographics are shown based on city and country."""
    )

col3, col4 = st.columns(2)
 
with col3:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
    sns.barplot(
        y="customer_count", 
        x="customer_city",
        data=customer_bycity_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by city", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
 
with col4:
    fig, ax = plt.subplots(figsize=(20, 10))
    
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
    sns.barplot(
        y="customer_count", 
        x="customer_state",
        data=customer_bystate_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by State", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

# Membuat Subheader Conclusion
st.subheader("Conclussion")

conclussions = ["The company's sales increase especially from December 2016 to November 2017. There was a decline until February 2018, but sales continued to improve until they peaked in August. The company experienced a very significant decline in sales in September and October. The company's income is in line with the ups and downs of sales.",
       'The product category with the highest sales is casa-mesa-banho and the product category with the lowest sales is pcs.',
       'The seller with the highest sales is the seller with ID 6560211a19b47992c3666cc44a7e94c0 and the seller with the highest income is the seller with ID 4a3ca9315b744ce9f8e9374361493884.',
       'The highest customer demographics by city are in Sao Paulo, and the highest customer demographics by country are in SP.']
s = ''

for i in conclussions:
    s += "- " + i + "\n"

st.markdown(s)