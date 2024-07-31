import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')

config = {
    'host': db_host,
    'port': db_port,
    'user': db_user,
    'password': db_pass,
    'database': db_name,
    #'cursorclass': mysql.connector.cursors.DictCursor  # Return results as dictionaries instead of tuples
}

try:
    connection = mysql.connector.connect(**config)
except (mysql.connector.Error, IOError) as err:
    print("Failed to connect to the database:", err)
    exit()
    
if connection and connection.is_connected():
    with connection.cursor() as cursor:
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        
        print("Query results:")
        for db in databases:
            print(db[0])
        
        cursor.close()
        connection.close()
        print("Database connection closed.")