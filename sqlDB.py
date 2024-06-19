import pysqlite3 as sqlite3

# def create_database_and_table():
#     conn = sqlite3.connect('users.db')
#     cursor = conn.cursor()

#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS responded_users (
#         user_id INTEGER PRIMARY KEY
#     )
#     ''')

#     conn.commit()
#     conn.close()

# def create_new_db():
#     conn = sqlite3.connect('config.db')
#     cursor = conn.cursor()

#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS information (
#         response_id INTEGER PRIMARY KEY,
#         response_text TEXT
#     )
#     ''')

#     conn.commit()
#     conn.close()

# if __name__ == "__main__":
#     create_new_db()
#     print("Database and table created successfully.")