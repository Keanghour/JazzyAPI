# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import BaseModel
# from typing import Optional
# import jwt
# import datetime

# app = FastAPI()

# # Define the OAuth2PasswordBearer instance
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Secret key and algorithm for encoding JWT
# SECRET_KEY = "mysecretkey"
# ALGORITHM = "HS256"

# class User(BaseModel):
#     username: str
#     password: str

# class UserInDB(User):
#     hashed_password: str

# # Simulate a database of users
# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "hashed_password": "fakehashedpassword"
#     }
# }

# def verify_password(plain_password, hashed_password):
#     return plain_password == hashed_password

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)

# def create_jwt_token(data: dict):
#     expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
#     to_encode = data.copy()
#     to_encode.update({"exp": expiration})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#         user = get_user(fake_users_db, username)
#         if user is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#         return user
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# @app.post("/token")
# def login(user: User):
#     db_user = get_user(fake_users_db, user.username)
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
#     token = create_jwt_token({"sub": user.username})
#     return {"access_token": token, "token_type": "bearer"}

# @app.get("/users/me")
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
