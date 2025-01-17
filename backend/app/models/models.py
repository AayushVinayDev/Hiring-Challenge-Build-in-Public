from pydantic import BaseModel, EmailStr
from typing import List, Dict, Union, Optional

class User(BaseModel):
    userId: str
    name: str
    email: str
    role: str
    xp: int = 0
    level: int = 1
    accuracy: float = 0.0

class ProgressionStep(BaseModel):
    max_addends: int
    target_number_range: List[int]

class GameConfig(BaseModel):
    name: str
    target_number_range: List[int]
    max_addends: int
    visual_feedback_sensitivity: float
    wrong_answer_messages: Dict[str, str]
    progression_path: List[ProgressionStep]

class Problem(BaseModel):
    target: int
    options: List[int]

# Auth models
class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str

class AuthResponse(BaseModel):
    token: str
    user: User