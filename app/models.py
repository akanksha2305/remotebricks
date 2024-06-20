# app/models.py

from pydantic import BaseModel, Field

# Pydantic model for user input validation
class User(BaseModel):
    username: str  # The username of the user
    email: str     # The email address of the user
    password: str  # The password of the user (will be hashed before storing in the database)

# Extended Pydantic model for user data stored in the database
class UserInDB(User):
    hashed_password: str  # The hashed version of the user's password
