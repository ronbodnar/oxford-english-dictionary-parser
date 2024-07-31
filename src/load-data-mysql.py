import os
from dotenv import load_dotenv
import mysql.connector
    
# The path to the file containing the data for insertion.
file = os.path.join(os.path.dirname(__file__), 'out.csv')

# Load the environment variables from .env files
load_dotenv()

# Set up the configuration dictionary for connecting to the database.
config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME'),
    'pool_size': 20,
    'allow_local_infile': 1,
}

# Try to connect to the MySQL database using mysql-connector-python.
try:
    connection = mysql.connector.connect(**config)
except (mysql.connector.Error, IOError) as err:
    print("Failed to connect to the database:", err)
    exit()

# Ensure the connection succeeded and is connected.
if connection and connection.is_connected():
    with connection.cursor() as cursor:
        cursor.execute(
            "LOAD DATA LOCAL INFILE %s " +
            "INTO TABLE oxford_words " +
            "FIELDS TERMINATED BY ',' " +
            "ENCLOSED BY '\"' " +
            "LINES TERMINATED BY '\n' " +
            "(text, snippet, parts_of_speech)", (file,))
        
        # Commit the change and close the connection.
        connection.commit()
        connection.close()
        
        print("Database connection closed.")
        
print("Done!")