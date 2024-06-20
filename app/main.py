# app/main.py

from fastapi import FastAPI, HTTPException, Depends, Body
from pymongo import MongoClient
from bson import ObjectId
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from typing import Optional, List
from dotenv import load_dotenv
import os
from .database import get_database

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))  # Use environment variable for MongoDB URI
db = client["user_database"]
users_collection = db["users"]

# Password hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models for user data validation
class User(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(User):
    hashed_password: str

# Utility function to hash a plain password
def hash_password(password: str):
    return pwd_context.hash(password)

# Utility function to verify a plain password against a hashed password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# API endpoint to register a new user
@app.post("/register", response_model=User)
async def register(user: User = Body(...)):
    # Check if the user with the provided email already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the user's password
    hashed_password = hash_password(user.password)
    
    # Convert the user data to a dictionary and add the hashed password
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    
    # Insert the new user into the database
    result = users_collection.insert_one(user_dict)
    
    # Assign the inserted ID to the user object
    user.id = str(result.inserted_id)
    
    return user

# API endpoint to log in a user
@app.post("/login")
async def login(email: str = Body(...), password: str = Body(...)):
    # Find the user by email
    user = users_collection.find_one({"email": email})
    
    # Check if the user exists and if the password is correct
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"message": "Login successful"}

# API endpoint to link an external ID to a user
@app.post("/link_id")
async def link_id(user_id: str = Body(...), external_id: str = Body(...)):
    # Update the user document with the external ID
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"external_id": external_id}}
    )
    
    # Check if the user was found and updated
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "ID linked successfully"}

# API endpoint to delete a user
@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: str):
    # Delete the user by ID
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    
    # Check if the user was found and deleted
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Additional logic to delete related data in other collections if needed
    
    return {"message": "User deleted successfully"}
