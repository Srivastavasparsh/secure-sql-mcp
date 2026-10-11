import sqlglot
from sqlglot import exp

class SQLSecurityException(Exception):
    """Raised when a query violates safety guardrails."""
    pass

class SQLGuardrail:
    FORBIDDEN_EXPRESSIONS = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,          # <--- updated from exp.AlterTable
        exp.Create,
        exp.TruncateTable,
    )

    @classmethod
    def validate_and_sanitize(cls, query: str) -> str:
        """
        Parses SQL using an Abstract Syntax Tree (AST).
        Guarantees:
        1. Query parses to valid SQL.
        2. Exactly one query is present (blocks stacked queries like 'SELECT 1; DROP TABLE users').
        3. Only read-only operations (SELECT) are permitted.
        """
        if not query or not query.strip():
            raise SQLSecurityException("Empty query provided.")

        try:
            parsed_statements = sqlglot.parse(query.strip())
        except sqlglot.errors.ParseError as e:
            raise SQLSecurityException(f"SQL Syntax Parse Error: {str(e)}")

        # Block multiple queries in a single execution (stacked queries)
        if len(parsed_statements) != 1:
            raise SQLSecurityException(
                f"Multiple statements detected ({len(parsed_statements)}). Stacked queries are prohibited."
            )

        statement = parsed_statements[0]
        if statement is None:
            raise SQLSecurityException("Failed to parse SQL statement.")

        # Traverse the entire AST to check for forbidden write/DDL nodes
        for node in statement.walk():
            if isinstance(node, cls.FORBIDDEN_EXPRESSIONS):
                raise SQLSecurityException(
                    f"Forbidden operation detected: {type(node).__name__}. Only read-only queries are allowed."
                )

        # Must evaluate to a Select expression
        if not isinstance(statement, (exp.Select, exp.Union)):
            raise SQLSecurityException(
                f"Query root must be a SELECT or UNION. Received: {type(statement).__name__}"
            )

        return statement.sql()