import sqlite3

connect = sqlite3.connect('user_data.db')
cursor = connect.cursor()

cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY , user_id INTEGER)""")

cursor.execute(
    """CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user_id INTEGER NULL, post_file_id TEXT NULL, post_text TEXT NULL)""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY,
    record REAL
)
""")


async def save_user(user_id):
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    connect.commit()


async def check_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    return user


async def post_file_id(post_file_id, user_id):
    cursor.execute("SELECT * FROM posts WHERE user_id = ?", (user_id,))
    post = cursor.fetchone()

    if post:
        cursor.execute("""UPDATE posts SET post_file_id = ? WHERE user_id = ?""", (post_file_id, user_id))
    else:
        cursor.execute("""INSERT INTO posts (user_id, post_file_id) VALUES (?, ?)""", (user_id, post_file_id))
    connect.commit()


async def post_text(user_id, post_text_content):
    cursor.execute("SELECT * FROM posts WHERE user_id = ?", (user_id,))
    post = cursor.fetchone()
    if post:
        cursor.execute("""UPDATE posts SET post_text = ? WHERE user_id = ?""", (post_text_content, user_id))
    else:
        cursor.execute("""INSERT INTO posts (user_id, post_text) VALUES (?, ?)""", (user_id, post_text_content))
    connect.commit()


async def user_post(user_id):
    cursor.execute("SELECT * FROM posts WHERE user_id = ?", (user_id,))
    post = cursor.fetchone()
    return post


