# src/server.py
import asyncio
from mcp.server.mcpserver import MCPServer as FastMCP
from src.db import init_db, get_schema_summary, execute_safe_query, get_query_plan
from src.guardrails import SQLSecurityException

mcp = FastMCP("Secure-Warehouse-Gateway")

@mcp.tool()
async def list_warehouse_schemas() -> str:
    """Lists all tables and their DDL schema definitions in the warehouse."""
    tables = await get_schema_summary()
    return "\n\n".join([f"Table: {t['table_name']}\nDDL: {t['schema']}" for t in tables])

@mcp.tool()
async def query_warehouse(sql: str) -> str:
    """
    Executes a read-only SQL query against the warehouse.
    Enforces AST security parsing to prevent mutations (INSERT, UPDATE, DELETE, DROP).
    """
    try:
        results = await execute_safe_query(sql)
        if not results:
            return "Query executed successfully. 0 records returned."
        return str(results)
    except SQLSecurityException as sec_err:
        return f"[SECURITY_VIOLATION]: {str(sec_err)}"
    except Exception as e:
        return f"[EXECUTION_ERROR]: {str(e)}"

@mcp.tool()
async def explain_query(sql: str) -> str:
    """
    Returns the EXPLAIN QUERY PLAN for a given read-only query to inspect indexes and scan efficiency.
    """
    try:
        plan = await get_query_plan(sql)
        return str(plan)
    except SQLSecurityException as sec_err:
        return f"[SECURITY_VIOLATION]: {str(sec_err)}"
    except Exception as e:
        return f"[PLAN_ERROR]: {str(e)}"

if __name__ == "__main__":
    asyncio.run(init_db())
    mcp.run()