import pytest
from src.guardrails import SQLGuardrail, SQLSecurityException

@pytest.mark.parametrize("malicious_query,expected_err", [
    ("DROP TABLE accounts;", "Forbidden operation detected: Drop"),
    ("DELETE FROM transactions WHERE 1=1;", "Forbidden operation detected: Delete"),
    ("UPDATE accounts SET balance = balance + 1000000;", "Forbidden operation detected: Update"),
    ("INSERT INTO accounts VALUES ('hacked', 'Attacker', 99999, 'Root');", "Forbidden operation detected: Insert"),
    ("SELECT * FROM accounts; DROP TABLE transactions;", "Multiple statements detected"),
    ("ALTER TABLE accounts ADD COLUMN backdoor TEXT;", "Forbidden operation detected: Alter"),  # <--- updated here
    ("TRUNCATE TABLE transactions;", "Forbidden operation detected: TruncateTable"),
    ("", "Empty query provided."),
])
def test_redteam_attacks_are_blocked(malicious_query, expected_err):
    with pytest.raises(SQLSecurityException) as excinfo:
        SQLGuardrail.validate_and_sanitize(malicious_query)
    assert expected_err in str(excinfo.value)

def test_benign_queries_pass():
    valid_query = "SELECT account_id, balance FROM accounts WHERE balance > 1000 ORDER BY balance DESC LIMIT 10;"
    sanitized = SQLGuardrail.validate_and_sanitize(valid_query)
    assert "SELECT" in sanitized
    assert "accounts" in sanitized