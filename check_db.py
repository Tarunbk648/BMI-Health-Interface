import sqlite3
db = sqlite3.connect('database.db')
cursor = db.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:", tables)
db.close()
