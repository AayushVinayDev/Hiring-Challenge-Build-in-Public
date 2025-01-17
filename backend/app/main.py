from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import List, Dict, Union, Optional
import json
import random
from models import GameConfig, User, SignUpRequest, LoginRequest, GoogleAuthRequest, AuthResponse, Problem
from auth import get_current_user

# Initialize FastAPI app
app = FastAPI(title="Balance Game API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin
cred = credentials.Certificate("firebase-credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize default game configuration
default_config = {
    "name": "Basic Addition",
    "target_number_range": [1, 10],
    "max_addends": 2,
    "visual_feedback_sensitivity": 0.7,
    "wrong_answer_messages": {
        "too_high": "Oops! Too much!",
        "too_low": "Not enough!",
        "far_off": "Try again!"
    },
    "progression_path": [
        {"max_addends": 2, "target_number_range": [1, 10]},
        {"max_addends": 2, "target_number_range": [5, 20]},
        {"max_addends": 3, "target_number_range": [10, 30]}
    ]
}


# Authentication endpoints
@app.post("/auth/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=request.email,
            password=request.password,
            display_name=request.name
        )

        # Create custom token for initial sign-in
        custom_token = auth.create_custom_token(user.uid)

        # Store user data in Firestore
        user_data = {
            "userId": user.uid,
            "name": request.name,
            "email": request.email,
            "role": request.role,
            "xp": 0,
            "level": 1,
            "accuracy": 0.0
        }
        db.collection('Users').document(user.uid).set(user_data)

        return AuthResponse(
            token=custom_token.decode('utf-8'),
            user=User(**user_data)
        )
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        # Get user by email
        user = auth.get_user_by_email(request.email)
        
        # Note: Firebase Admin SDK cannot verify passwords
        # In a production environment, you would use Firebase Client SDK
        # Here we're creating a custom token for demonstration
        custom_token = auth.create_custom_token(user.uid)

        # Get user data from Firestore
        user_doc = db.collection('Users').document(user.uid).get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User data not found"
            )

        return AuthResponse(
            token=custom_token.decode('utf-8'),
            user=User(**user_doc.to_dict())
        )
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/auth/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest):
    try:
        # Verify the Google ID token
        decoded_token = auth.verify_id_token(request.id_token)
        uid = decoded_token['uid']

        # Check if user exists in Firestore
        user_doc = db.collection('Users').document(uid).get()
        
        if not user_doc.exists:
            # Create new user document if first time sign in
            user_data = {
                "userId": uid,
                "name": decoded_token.get('name', ''),
                "email": decoded_token.get('email', ''),
                "role": "student",  # Default role
                "xp": 0,
                "level": 1,
                "accuracy": 0.0
            }
            db.collection('Users').document(uid).set(user_data)
        else:
            user_data = user_doc.to_dict()

        # Create custom token for session
        custom_token = auth.create_custom_token(uid)

        return AuthResponse(
            token=custom_token.decode('utf-8'),
            user=User(**user_data)
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Existing endpoints
@app.get("/")
async def root():
    return {"message": "Balance Game API is running"}

@app.get("/config/{config_id}")
async def get_game_config(config_id: str):
    doc_ref = db.collection('GameConfigurations').document(config_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return doc.to_dict()

@app.get("/user/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    doc_ref = db.collection('Users').document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="User not found")
    return doc.to_dict()

@app.post("/user")
async def create_user(user: User, current_user: dict = Depends(get_current_user)):
    try:
        user_ref = db.collection('Users').document(user.userId)
        user_ref.set(user.dict())
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)