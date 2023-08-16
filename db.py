import psycopg2
import os
from dotenv import load_dotenv

# Define the global connection variable and initialize it to None
connection = None
load_dotenv()


def init_connection():
    """
    Initializes the connection to the PostgreSQL database when the module is imported.
    Adjust the connection parameters as per your PostgreSQL setup.
    """
    global connection
    if connection is None:
        try:
            connection = psycopg2.connect(
                database=os.environ.get("POSTGRES_DB"),
                user=os.environ.get("POSTGRES_USER"),
                password=os.environ.get("POSTGRES_PASSWORD"),
                #host=os.environ.get("POSTGRES_HOST"),
                host="db",
                port=os.environ.get("POSTGRES_PORT")
            )
            print("Connected to the PostgreSQL database successfully.")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL:", error)


def close_connection():
    """
    Closes the database connection if it's open.
    """
    global connection
    if connection is not None:
        connection.close()
        print("Database connection closed.")
        connection = None

