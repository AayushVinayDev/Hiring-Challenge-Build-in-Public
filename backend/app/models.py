from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional

class User(BaseModel):
    userId: str
    name: str
    email: str
    role: str
    xp: int = 0
    level: int = 1
    accuracy: float = 0.0

class UserProgress(BaseModel):
    userId: str
    name: str
    level: int
    xp: int
    accuracy: float
    role: str

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

class AnswerSubmission(BaseModel):
    problemId: str
    userAnswer: List[int]
    correctAnswer: int
    userId: str

class AnswerResponse(BaseModel):
    correct: bool
    user: User
    message: str

# Auth related models
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