# 🌌 Retail Pulse Pro: Advanced Analytics Dashboard

An enterprise-grade, interactive retail analytics dashboard built with **Streamlit**, **Plotly**, and **Python**. This project transforms raw database transactions into actionable business intelligence using high-performance SQL querying, interactive visualizations, and a custom-styled modern dark-mode UI.


## ✨ Key Features

* **Modern Custom UI/UX:** Utilizes custom CSS injection to override Streamlit's default styling, featuring glowing text, floating metric cards with hover animations, and a seamless dark mode.
* **Dynamic KPI Engine:** Instantly calculates Gross Revenue, Total Transactions, Unique Customers, and Average Order Value (AOV) based on active filters.
* **Advanced Visualizations (Plotly):**
    * 📈 **Revenue Trajectory:** Smooth area charts mapping sales over time.
    * 📦 **Category Share:** Interactive donut charts for product distribution.
    * 🔥 **Sales Intensity Heatmap:** Density matrix showing the best-selling categories by day of the week.
    * 👥 **Demographics:** Stacked horizontal bar charts breaking down buyer gender per category.
* **High-Performance Architecture:** * Uses **SQLAlchemy** for robust, parameterized database connections to prevent SQL injection.
    * Implements Streamlit's `@st.cache_data` with Time-to-Live (TTL) to minimize database load and ensure fast rendering.
* **Smart Data Grids:** Transaction ledgers featuring Pandas `background_gradient` styling for immediate visual identification of high-value orders.

## 🛠️ Tech Stack

* **Frontend / Framework:** [Streamlit](https://streamlit.io/)
* **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
* **Visualizations:** [Plotly Express](https://plotly.com/python/plotly-express/)
* **Database ORM / Connector:** [SQLAlchemy](https://www.sqlalchemy.org/)
* **Language:** Python 3.9+

## 🚀 Getting Started

### Prerequisites

Ensure you have Python installed, along with access to a SQL database (PostgreSQL, MySQL, SQLite, etc.) containing your `retail_sales` table.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/retail-pulse-pro.git](https://github.com/yourusername/retail-pulse-pro.git)
   cd retail-pulse-pro
