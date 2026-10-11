import asyncio
from src.db import init_db, execute_safe_query

async def main():
    # 1. Initialize and seed tables if they do not exist yet
    await init_db()
    
    # 2. Query the seeded records
    accounts = await execute_safe_query("SELECT * FROM accounts;")
    transactions = await execute_safe_query("SELECT * FROM transactions;")
    
    print("\n--- DATABASE VERIFICATION SUCCESS ---")
    print(f"Accounts found ({len(accounts)}):")
    for acc in accounts:
        print(f"  -> {acc['account_id']} | {acc['holder_name']} | Balance: ${acc['balance']}")

    print(f"\nTransactions found ({len(transactions)}):")
    for tx in transactions:
        print(f"  -> {tx['tx_id']} | Account: {tx['account_id']} | Amount: ${tx['amount']} | Status: {tx['status']}")
    print("---------------------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())