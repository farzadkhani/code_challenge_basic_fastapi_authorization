from fastapi import FastAPI, HTTPException, Depends, Cookie, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# User model to represent user data
class User(BaseModel):
    username: str
    password: str

# Sample user data stored in memory
users_db = {
    "user1": {
        "password": "test1"
    },
    "user2": {
        "password": "test2"
    }
}

@app.post("/register/", status_code=status.HTTP_201_CREATED)
def register(user: User):
    '''
    registration user api
    '''

    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
    users_db[user.username] = {"password": user.password}
    return {"message": "User registered successfully"}

# Model to represent user data without password
class UserWithoutPassword(BaseModel):
    """
    return user without password
    """

    username: str


# get list of user from db
@app.get(
    "/users/", 
    response_model=list[UserWithoutPassword]
)
def get_users():
    '''
    get list of users api
    '''

    users_list = [
        UserWithoutPassword(
            username=username,
        ) for username in users_db.keys()
    ]
    return users_list


def authenticate_user(user_obj):
    '''
    authentication user
    '''

    username = user_obj.username
    password = user_obj.password
    if username in users_db and password == users_db[username]["password"]:
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )


@app.post("/login/")
def login(user: User, response: JSONResponse):
    '''
    login user api
    '''

    authenticated_user = authenticate_user(user)
    if authenticated_user != user.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    response.set_cookie(key="username", value=user.username)
    return {"message": "Login successful"}


@app.post("/logout/")
def logout(response: JSONResponse, username: str = Cookie(None)):
    '''
    logout user api
    '''

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in",
        )
    response.delete_cookie(key="username")
    return {"message": "Logout successful"}
