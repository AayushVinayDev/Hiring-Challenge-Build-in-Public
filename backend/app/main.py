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

def generate_problem(config: GameConfig) -> Problem:
    """
    Generate a new problem based on the game configuration.
    Ensures there are exactly two correct combinations in the options.
    """
    min_num, max_num = config.target_number_range
    target = random.randint(min_num, max_num)
    
    # Generate all possible pairs that sum to target within the range
    valid_pairs = []
    for i in range(min_num, max_num + 1):
        complement = target - i
        if min_num <= complement <= max_num and i <= complement:
            valid_pairs.append((i, complement))
    
    # If we can't find at least two valid pairs, adjust the target
    attempts = 0
    while len(valid_pairs) < 2 and attempts < 10:
        target = random.randint(min_num, max_num)
        valid_pairs = []
        for i in range(min_num, max_num + 1):
            complement = target - i
            if min_num <= complement <= max_num and i <= complement:
                valid_pairs.append((i, complement))
        attempts += 1
    
    # If we still can't find valid pairs, create artificial ones just outside the range
    if len(valid_pairs) < 2:
        # Create one valid pair within range
        num1 = random.randint(min_num, target - min_num)
        valid_pairs = [(num1, target - num1)]
        # Add one more valid pair (might be slightly outside range)
        num2 = random.randint(min_num, target - min_num)
        while num2 == num1:
            num2 = random.randint(min_num, target - min_num)
        valid_pairs.append((num2, target - num2))
    
    # Select two random valid pairs for our correct options
    selected_pairs = random.sample(valid_pairs, 2)
    options = list(selected_pairs[0] + selected_pairs[1])
    
    # Generate additional options to have 5 total
    while len(options) < 5:
        new_num = random.randint(min_num, max_num)
        # Ensure the new number doesn't create another valid sum
        if new_num not in options and (target - new_num) not in options:
            options.append(new_num)
    
    # Shuffle the options
    random.shuffle(options)
    
    return Problem(target=target, options=options)

@app.on_event("startup")
async def startup_event():
    # Create default game configuration if it doesn't exist
    config_ref = db.collection('GameConfigurations').document('default')
    if not config_ref.get().exists:
        config_ref.set(default_config)

@app.get("/game/problem", response_model=Problem)
async def get_game_problem(current_user: dict = Depends(get_current_user)):
    """
    Generate a new problem based on the current game configuration.
    This endpoint requires authentication.
    """
    try:
        # Get the current game configuration
        config_ref = db.collection('GameConfigurations').document('default')
        doc = config_ref.get()
        
        if not doc.exists:
            config_ref.set(default_config)
            config = GameConfig(**default_config)
        else:
            config = GameConfig(**doc.to_dict())
        
        # Generate and return the problem
        problem = generate_problem(config)
        return problem
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating problem: {str(e)}"
        )

# Game configuration endpoint
@app.get("/game/config", response_model=GameConfig)
async def get_game_config(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the default game configuration from Firestore.
    This endpoint requires authentication.
    """
    try:
        config_ref = db.collection('GameConfigurations').document('default')
        doc = config_ref.get()
        
        if not doc.exists:
            # If default config doesn't exist (shouldn't happen due to startup event)
            # create it and return
            config_ref.set(default_config)
            return GameConfig(**default_config)
            
        return GameConfig(**doc.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving game configuration: {str(e)}"
        )


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