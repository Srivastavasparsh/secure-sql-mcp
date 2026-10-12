# app.py
import streamlit as st
import asyncio
import pandas as pd
from src.db import init_db, execute_safe_query
from src.guardrails import SQLSecurityException

# Page configuration
st.set_page_config(page_title="Secure Database Gateway", page_icon="🛡️")

# Initialize the database asynchronously
@st.cache_resource
def setup_database():
    asyncio.run(init_db())
    return True

setup_database()

st.title("🛡️ Secure AI Database Gateway")
st.markdown("""
**AST-Based SQL Guardrails Demonstration**
This interface simulates an AI agent attempting to query a financial database. The backend uses `sqlglot` to parse queries into an Abstract Syntax Tree (AST), blocking all mutations (`DROP`, `INSERT`, `UPDATE`) and stacked queries regardless of prompt injections.
""")

st.subheader("Test the Guardrails")
st.markdown("Try a read-only query like `SELECT * FROM accounts;` or an attack like `DROP TABLE accounts;`")

query = st.text_area("SQL Input:", "SELECT * FROM accounts;")

if st.button("Execute Query"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        try:
            # Execute safely using your existing async database logic
            results = asyncio.run(execute_safe_query(query))
            st.success("✅ Query verified and executed successfully.")
            
            if results:
                # Render results beautifully using Pandas
                st.dataframe(pd.DataFrame(results), use_container_width=True)
            else:
                st.info("Query returned 0 rows.")
                
        except SQLSecurityException as sec_err:
            st.error(f"🚨 **[SECURITY_VIOLATION]**\n\n{str(sec_err)}")
        except Exception as e:
            st.warning(f"⚠️ **[EXECUTION_ERROR]**\n\n{str(e)}")