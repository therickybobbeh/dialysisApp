import psycopg2

conn = psycopg2.connect(
    dbname="pd_management",
    user="postgres",
    password="admin",
    host="localhost",
    port=5432
)

cur = conn.cursor()

# Example: Insert a single row
cur.execute("""
    INSERT INTO users (id, name, email, password, role)
    VALUES (%s, %s, %s, %s, %s)
""", (1, 'Alice', 'alice@example.com', 'password123', 'admin'))

# Example: Insert multiple rows
users = [
    (2, 'Bob', 'bob@example.com', 'password456', 'user'),
    (3, 'Carol', 'carol@example.com', 'password789', 'user'),
]
cur.executemany("""
    INSERT INTO users (id, name, email, password, role)
    VALUES (%s, %s, %s, %s, %s)
""", users)

conn.commit()
cur.close()
conn.close()
