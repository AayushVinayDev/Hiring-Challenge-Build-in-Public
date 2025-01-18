from fastapi import APIRouter, HTTPException, status
from firebase_admin import auth
from app.models import SignUpRequest, LoginRequest, GoogleAuthRequest, AuthResponse, User

router = APIRouter()

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    try:
        user = auth.create_user(
            email=request.email,
            password=request.password,
            display_name=request.name
        )

        custom_token = auth.create_custom_token(user.uid)
        
        from app.database import db
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

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        user = auth.get_user_by_email(request.email)
        custom_token = auth.create_custom_token(user.uid)

        from app.database import db
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

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest):
    try:
        decoded_token = auth.verify_id_token(request.id_token)
        uid = decoded_token['uid']

        from app.database import db
        user_doc = db.collection('Users').document(uid).get()
        
        if not user_doc.exists:
            user_data = {
                "userId": uid,
                "name": decoded_token.get('name', ''),
                "email": decoded_token.get('email', ''),
                "role": "student",
                "xp": 0,
                "level": 1,
                "accuracy": 0.0
            }
            db.collection('Users').document(uid).set(user_data)
        else:
            user_data = user_doc.to_dict()

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