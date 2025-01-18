from fastapi import APIRouter, HTTPException, Depends, status
from app.models import GameConfig, Problem, AnswerSubmission, AnswerResponse, User
from app.services.game_service import generate_problem, check_answer, update_user_progress
from app.auth import get_current_user
from app.config import default_game_config

router = APIRouter()

@router.get("/config", response_model=GameConfig)
async def get_game_config(current_user: dict = Depends(get_current_user)):
    """
    Retrieve the default game configuration from Firestore.
    """
    try:
        from app.database import db
        config_ref = db.collection('GameConfigurations').document('default')
        doc = config_ref.get()
        
        if not doc.exists:
            config_ref.set(default_game_config)
            return GameConfig(**default_game_config)
            
        return GameConfig(**doc.to_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving game configuration: {str(e)}"
        )

@router.get("/problem", response_model=Problem)
async def get_game_problem(current_user: dict = Depends(get_current_user)):
    """
    Generate a new problem based on the current game configuration.
    """
    try:
        from app.database import db
        config_ref = db.collection('GameConfigurations').document('default')
        doc = config_ref.get()
        
        if not doc.exists:
            config_ref.set(default_game_config)
            config = GameConfig(**default_game_config)
        else:
            config = GameConfig(**doc.to_dict())
        
        return generate_problem(config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating problem: {str(e)}"
        )

@router.post("/submit", response_model=AnswerResponse)
async def submit_answer(
    submission: AnswerSubmission,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit an answer and update user progress.
    """
    try:
        from app.database import db
        
        # Verify user exists
        user_ref = db.collection('Users').document(submission.userId)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get current user data
        user_data = user_doc.to_dict()
        user = User(**user_data)
        
        # Check answer and update progress
        is_correct = check_answer(submission)
        updated_user = update_user_progress(user, is_correct)
        
        # Save updated user data
        user_ref.set(updated_user.dict())
        
        # Prepare response message
        message = "Correct! Keep up the good work!" if is_correct else "Not quite right. Try again!"
        
        return AnswerResponse(
            correct=is_correct,
            user=updated_user,
            message=message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing answer submission: {str(e)}"
        )