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
