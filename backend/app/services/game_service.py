import random
from typing import Tuple
from app.models import GameConfig, Problem, User, AnswerSubmission

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
    
    # If we still can't find valid pairs, create artificial ones
    if len(valid_pairs) < 2:
        num1 = random.randint(min_num, target - min_num)
        valid_pairs = [(num1, target - num1)]
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
        if new_num not in options and (target - new_num) not in options:
            options.append(new_num)
    
    random.shuffle(options)
    return Problem(target=target, options=options)

def check_answer(submission: AnswerSubmission) -> bool:
    """
    Check if the user's answer is correct.
    """
    return sum(submission.userAnswer) == submission.correctAnswer

def calculate_level_xp(level: int) -> Tuple[int, int]:
    """
    Calculate XP required for the current level and next level.
    Returns (xp_for_current_level, xp_for_next_level)
    """
    base_xp = 100
    xp_for_current = base_xp * (level - 1)
    xp_for_next = base_xp * level
    return xp_for_current, xp_for_next

def update_user_progress(user: User, correct: bool) -> User:
    """
    Update user's XP, level, and accuracy based on their answer.
    """
    # Update total attempts for accuracy calculation
    total_attempts = user.xp // 10  # Each attempt is worth 10 XP
    correct_attempts = int(user.accuracy * total_attempts)
    
    if correct:
        # Add XP for correct answer
        user.xp += 10
        correct_attempts += 1
    
    # Update accuracy
    total_attempts += 1
    user.accuracy = correct_attempts / total_attempts if total_attempts > 0 else 0.0
    
    # Check for level up
    current_level_xp, next_level_xp = calculate_level_xp(user.level)
    while user.xp >= next_level_xp:
        user.level += 1
        current_level_xp, next_level_xp = calculate_level_xp(user.level)
    
    return user