# 📊 SQL Chat + Auto Plot with Groq + LangChain + Streamlit

An **AI-powered SQL-to-Plot Generator** using **LangChain**, **Groq Llama 3**, and **Streamlit**. Query your MySQL database in **plain English**, automatically generate **SQL queries**, and visualize data **instantly** with dynamic plots.

---

## 🚀 Features

✅ Connect securely to **MySQL** database  
✅ Ask natural language questions → Get SQL queries → See results  
✅ **Auto-generate charts** with **Plotly** (Bar, Line, Pie, etc.)  
✅ Supports **JOINs**, aggregations, and filters in queries  
✅ View and debug **generated Python code** before execution  
✅ Powered by **LangChain Agent Toolkit** and **Groq’s ultra-fast Llama 3** models  
✅ Built with **Streamlit** for a fast, interactive web interface

---

## 📷 Demo Screenshot

![image](https://github.com/user-attachments/assets/38bcceba-a89f-455e-8486-443eae735d33)
 <!-- Replace with your own screenshot -->

---

## 🏗️ Architecture

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

```
### 2️⃣ Install dependencies
```
pip install -r requirements.txt
```
### 3️⃣ Run the Streamlit app
```
streamlit run app.py
```
### ⚙️ Usage
📝 Enter your MySQL database credentials in the sidebar.

🔑 Provide your Groq API key (Get from https://console.groq.com/).

🔌 Click Connect.

💬 Ask queries like:

Plot total number of orders per product

Show average spending by customer name

Plot monthly revenue trend for each product category

📊 View interactive visualizations instantly.

### 🔧 Tech Stack
Python 3.9+

Streamlit – Frontend interface

LangChain – AI agent framework

Groq API (Llama 3 8b) – LLM for SQL & Python generation

MySQL – Relational database

Pandas – Data manipulation

Plotly – Interactive visualization

### 📜 Example .env (Optional)
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DB=yourdatabase
GROQ_API_KEY=your_groq_api_key
```

