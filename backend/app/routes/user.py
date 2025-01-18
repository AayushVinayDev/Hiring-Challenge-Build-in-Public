from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from app.models import User, UserProgress
from app.auth import get_current_user

router = APIRouter()

@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve user data from Firestore.
    """
    from app.database import db
    doc_ref = db.collection('Users').document(user_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return doc.to_dict()

@router.get("/{user_id}/progress", response_model=UserProgress)
async def get_user_progress(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> UserProgress:
    """
    Retrieve user progress data from Firestore.
    Only teachers can access other users' progress.
    Students can only access their own progress.
    """
    try:
        from app.database import db
        
        # Check if the requesting user has permission to access this data
        if current_user['uid'] != user_id and current_user.get('role') != 'teacher':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this user's progress"
            )
        
        # Get user data from Firestore
        user_ref = db.collection('Users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        return UserProgress(
            userId=user_id,
            name=user_data['name'],
            level=user_data['level'],
            xp=user_data['xp'],
            accuracy=user_data['accuracy'],
            role=user_data['role']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user progress: {str(e)}"
        )

@router.post("/", response_model=Dict[str, str])
async def create_user(
    user: User,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Create a new user in Firestore.
    """
    try:
        from app.database import db
        user_ref = db.collection('Users').document(user.userId)
        user_ref.set(user.dict())
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )