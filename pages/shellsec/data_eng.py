import sqlite3
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('shellsec.pw/shellsec.db')
cursor = conn.cursor()

# Select all elements from the "posts" table
cursor.execute("SELECT id, author, body, timestamp, url FROM posts")
posts = cursor.fetchall()

for post in posts:
    id, author, body, timestamp, url = post
    
    # Extract the thread name from the URL
    thread_name = url.split('/')[-1].split('?')[0]
    
    # Convert the datetime string to epoch time
    datetime_obj = datetime.strptime(timestamp, '%d-%m-%Y, %H:%M')
    epoch_time = int(datetime_obj.timestamp())
    
    # Update the existing row with the computed values
    cursor.execute("UPDATE posts SET epoch_time = ?, thread_name = ? WHERE id = ?", (epoch_time, thread_name, id))

# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()
