# src/db.py
import aiosqlite
from typing import List, Dict, Any, Tuple
from src.guardrails import SQLGuardrail

DB_PATH = "warehouse.db"

async def init_db():
    """Seeds a dummy enterprise warehouse ledger."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                holder_name TEXT NOT NULL,
                balance REAL NOT NULL,
                tier TEXT NOT NULL
            );
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                tx_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            );
        """)
        # Seed test records if empty
        cursor = await db.execute("SELECT COUNT(*) FROM accounts;")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.execute("INSERT INTO accounts VALUES ('acc_01', 'Acme Corp', 52400.50, 'Enterprise');")
            await db.execute("INSERT INTO accounts VALUES ('acc_02', 'Beta Global', 12300.00, 'Standard');")
            await db.execute("INSERT INTO transactions VALUES ('tx_101', 'acc_01', -1500.00, datetime('now'), 'COMPLETED');")
            await db.execute("INSERT INTO transactions VALUES ('tx_102', 'acc_01', 5000.00, datetime('now'), 'COMPLETED');")
            await db.commit()

async def get_schema_summary() -> List[Dict[str, Any]]:
    """Returns schemas of all available tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        rows = await cursor.fetchall()
        return [{"table_name": r[0], "schema": r[1]} for r in rows]

async def execute_safe_query(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
    """Validates the query using AST guardrails before execution."""
    sanitized_sql = SQLGuardrail.validate_and_sanitize(query)
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sanitized_sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_query_plan(query: str) -> List[Dict[str, Any]]:
    """Explains the execution plan without mutating data."""
    sanitized_sql = SQLGuardrail.validate_and_sanitize(query)
    explain_sql = f"EXPLAIN QUERY PLAN {sanitized_sql}"
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(explain_sql) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]