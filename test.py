import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from langchain_groq import ChatGroq
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.streamlit import StreamlitCallbackHandler
import re

st.set_page_config(page_title="🗂️ SQL to Plot with LLM", page_icon="📊")
st.title("📊 SQL Chat + Auto Plot with Groq + LangChain")

# ---------------- Sidebar Inputs ---------------- #
st.sidebar.header("Database Connection")
mysql_host = st.sidebar.text_input("MySQL Host")
mysql_user = st.sidebar.text_input("MySQL User")
mysql_password = st.sidebar.text_input("MySQL Password", type="password")
mysql_db = st.sidebar.text_input("MySQL Database")

st.sidebar.header("Groq API Key")
groq_api_key = st.sidebar.text_input("Groq API Key", type="password")

@st.cache_resource(ttl="2h")
def connect_to_sqlalchemy(mysql_host, mysql_user, mysql_password, mysql_db):
    url = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
    engine = create_engine(url)
    return engine, SQLDatabase(engine)


# Connect button
if st.sidebar.button("Connect"):
    if mysql_host and mysql_user and mysql_password and mysql_db and groq_api_key:
        try:
            engine, db = connect_to_sqlalchemy(mysql_host, mysql_user, mysql_password, mysql_db)
            st.session_state.engine = engine
            st.session_state.db = db
            st.session_state.llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.3-70b-versatile", streaming=True)
            st.success(f"✅ Connected to `{mysql_db}` successfully")
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")
# Helper SQL function
def run_sql_query(query):
    with st.session_state.engine.connect() as conn:
        return pd.read_sql(query, conn)

# ---------------- Custom Tool for Plot Generation ---------------- #
from langchain.tools import BaseTool
class PlotGenerationTool(BaseTool):
    name: str = "Plot Generation Tool"
    description: str = """
    Generates Python code to create visualizations using Pandas & Plotly for Streamlit.
    Handles JOIN queries across tables automatically if required.
    Input example: 'Plot total spending by customer from orders table'
    """
    def _run(self, query: str) -> str:
        try:
            instruction_prompt = f"""
            You are an expert Python and SQL assistant specialized in generating data visualizations from SQL databases for Streamlit applications.

            Instructions:

            1. SQL Query Generation:
            - ALWAYS use the function run_sql_query("<SQL QUERY>") to query the database.
            - NEVER use pd.read_sql() or direct database connectors.
            - If multiple tables are required, automatically generate JOINs assuming standard foreign key relationships (e.g., orders.product_id = products.product_id).
            - Use meaningful GROUP BY clauses for aggregation.

            2. Chart Library and Chart Selection:
            - By default, use Plotly Express (px) for all visualizations.
            - IF the user explicitly mentions matplotlib, seaborn, or pyplot → generate the chart using that requested library.
            - For matplotlib/seaborn → use standard import conventions:
                - matplotlib → import matplotlib.pyplot as plt
                - seaborn → import seaborn as sns
            - Use st.pyplot(fig) or st.pyplot() for rendering in Streamlit.
            - Ensure charts from matplotlib/seaborn are also well-labeled and aesthetically pleasing.
            - If the user specifies a chart type (e.g., bar, line, pie, scatter, histogram), generate that chart type.
            - If no chart type is specified, automatically determine the most suitable chart type based on data:
            - Categorical + Aggregated numeric → Bar chart
            - Time series → Line chart
            - Two continuous variables → Scatter plot
            - Distribution of single variable → Histogram
            - Percentage composition → Pie chart

            3. Chart Styling:
            - Make charts aesthetically good, well-labeled, and easy to interpret.
            - Add axis labels, chart title, legends, color schemes.
            - Rotate x-axis labels for readability if needed.
            - For Plotly charts → use fig.update_layout() to adjust layout, fonts, titles, and legends.
            - For matplotlib/seaborn charts → use plt.title(), plt.xlabel(), plt.ylabel(), sns.set_style(), or similar functions.

            4. Streamlit Display:
            - For Plotly → use st.plotly_chart(fig)
            - For Matplotlib/Seaborn → use st.pyplot(fig) or st.pyplot()

            5. Output Format:
            - ALWAYS output a COMPLETE Python code snippet ONLY.
            - Wrap the entire output inside triple backticks (```).
            - DO NOT provide any explanation, markdown text, or anything else outside the code block.
            - The output must be a fully runnable code block for Streamlit.

            Example for Plotly Express:

            ```python
            df = run_sql_query(\"""
                SELECT c.category_name, SUM(o.amount) as total_revenue
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                JOIN categories c ON p.category_id = c.category_id
                GROUP BY c.category_name
            \""")
            fig = px.pie(df, names="category_name", values="total_revenue", title="Total Revenue by Category")
            fig.update_layout(title_font_size=22, legend_title="Category")
            st.plotly_chart(fig)

            USER REQUEST: {query}
            """

            response = st.session_state.llm.predict(instruction_prompt)

            # ✅ Strip and extract clean Python code block
            code_blocks = re.findall(r"```python(.*?)```", response, re.DOTALL)

            if code_blocks:
                code = code_blocks[0].strip()
            else:
                # Fallback if no triple backtick found, use entire response
                code = response.strip()

            # 🔎 Show generated code for debugging
            code = code.replace(') fig =', ')\nfig =')
            code = code.replace(') st.plotly_chart', ')\nst.plotly_chart')
            with st.expander("Generated Code", expanded=True):
                st.code(code, language="python")

            # ⚠️ Strip accidental markdown or leading/trailing quotes/backticks manually
            code = re.sub(r"^\s*python\s*", "", code.strip())
            print(code)

            # ✅ Run the code → Capture SyntaxError for feedback
            try:
                st.code(code, language="python")  # ✅ Display the code in UI, easier than print()

                compiled_code = compile(code, "<string>", "exec")

                exec(compiled_code, globals())
            except SyntaxError as e:
                st.error(f"❌ Syntax Error:\n\n{e}\n\nProblematic code:\n{code}")
                return "❌ Code execution failed due to syntax error."
            except Exception as e:
                st.error(f"❌ Execution Error:\n\n{e}\n\nCode was:\n{code}")
                return "❌ Code execution failed."

            return "✅ Plot generated successfully."

        except Exception as e:
            return f"❌ Tool error: {e}"

    def _arun(self, query: str):
        raise NotImplementedError("Async execution not supported.")

# ---------------- Initialize Agent if connected ---------------- #
if "db" in st.session_state and "llm" in st.session_state:
    sql_toolkit = SQLDatabaseToolkit(db=st.session_state.db, llm=st.session_state.llm)
    tools = sql_toolkit.get_tools() + [PlotGenerationTool()]

    callback_handler = StreamlitCallbackHandler(st.container())

    agent = initialize_agent(
        tools=tools,
        llm=st.session_state.llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        callbacks=[callback_handler],
        handle_parsing_errors=True,
    )

    st.header("📝 Ask your database or request plots:")
    user_prompt = st.chat_input("e.g., Plot total spending by customer from orders table...")

    if user_prompt:
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.chat_message("assistant"):
            result = agent.run(user_prompt)
            st.success(result)
