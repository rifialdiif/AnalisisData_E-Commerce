# Proyek Analisis Data: E-Commerce Public Dataset 📊

Welcome to the **E-Commerce Data Analysis** project repository! This project is the final assessment for the Data Analysis course, where I perform an end-to-end analysis on the Olist E-Commerce Public Dataset.

---

## 👤 Author Information
- **Name:** Rifialdi Faturrochman
- **Identity:** Fresh Graduate in Software Engineering
- **Personal Branding:** **RF Dashboard** 🚀

---

## 📝 Project Description
This project focuses on analyzing the **Olist E-Commerce Public Dataset**, which contains information on 100k orders from 2016 to 2018 in Brazil. The primary objective is to extract actionable insights through a complete data science workflow:
1. **Data Wrangling:** Gathering, assessing, and cleaning the data.
2. **Exploratory Data Analysis (EDA):** Identifying patterns and relationships.
3. **Data Visualization:** Creating intuitive charts to answer business questions.
4. **Dashboarding:** Building an interactive dashboard for stakeholders.

---

## ❓ Key Business Questions
1. Which product categories contribute the most revenue and how is their customer satisfaction level?
2. Where are the customers geographically concentrated, and how efficient is the delivery process (Actual vs. Estimated)?
3. How is the customer segmentation based on **RFM Analysis** (Recency, Frequency, Monetary)?

---

## 💡 Key Insights & Findings

### 1. Revenue & Satisfaction
- **Health & Beauty** emerged as the top revenue-generating category.
- Most top-performing categories also maintain a **high satisfaction level**, indicating a strong correlation between product quality and market performance.

### 2. Geolocation & Logistics Efficiency
- Customers are heavily concentrated in **São Paulo (SP)**.
- Logistics in São Paulo are the most efficient, showing the shortest gap between actual delivery dates and estimated arrival times.

### 3. RFM Analysis Results
- The segmentation revealed that the **At Risk / Hibernating** segment is currently the largest.
- **Action Required:** There is a critical need for targeted retention strategies (e.g., personalized discounts or re-engagement emails) to win back these customers.

---

## 🛠 Tech Stack
| Tool/Library | Usage |
| :--- | :--- |
| **Python** | Core programming language |
| **Pandas** | Data manipulation and analysis |
| **Matplotlib / Seaborn** | Static data visualization |
| **Plotly** | Interactive visualizations |
| **Streamlit** | Dashboard deployment |

---

## 📁 Project Structure
```text
.
├── dashboard/
│   └── dashboard.py       # Main file for the Streamlit dashboard
├── data/                  # Directory containing raw CSV files
├── notebook.ipynb         # Jupyter Notebook for EDA & Wrangling
├── requirements.txt       # Dependencies list
└── README.md              # Project documentation
```

---

## 🚀 Installation & Running

### 1. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run dashboard/dashboard.py
```

---

## 🎯 Conclusion
To maximize growth, the business should focus on scaling the **Health & Beauty** segment while aggressively implementing retention campaigns for **At Risk** customers. Improving logistics in regions outside São Paulo by mirroring the SP hub's efficiency could further boost customer satisfaction.

---

*Developed with ❤️ by Rifialdi Faturrochman | RF Dashboard*
