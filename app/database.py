# app/database.py

from pymongo import MongoClient

def get_database():
    """
    Establish a connection to the MongoDB server and return the user database.

    This function initializes a connection to the MongoDB server using the
    MongoClient. The connection string is used to connect to a MongoDB Atlas 
    cluster. The client then accesses the specific database, in this case 
    'user_database', and returns it.

    Returns:
        Database: The 'user_database' database from the MongoDB server.
    """
    # Initialize the MongoClient with the connection string to the MongoDB Atlas cluster
    client = MongoClient("mongodb+srv://akanksha:<password>@cluster1.ivbueeg.mongodb.net/")
    
    # Access the 'user_database' database
    return client["user_database"]
