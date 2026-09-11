"""
FSRS spaced repetition algorithm.
"""

from datetime import datetime, timedelta
from fsrs import Scheduler, Card, Rating
import logging
import time

logger = logging.getLogger(__name__)

# Initialize FSRS scheduler with default parameters
scheduler = Scheduler()

def rating_to_fsrs_rating(rating: int) -> Rating:
    """Convert our 1-4 rating to FSRS Rating enum."""
    # Our rating: 1=Again, 2=Hard, 3=Good, 4=Easy
    # FSRS Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
    return Rating(rating)

def fsrs_update(card_data: dict, rating: int) -> dict:
    """
    Apply FSRS algorithm and return updated fields.
    
    Args:
        card_data: Dictionary containing current card state
            - stability: float or None
            - difficulty: float or None
            - due: datetime or None
            - last_review: datetime or None
            - state: int (FSRS State enum value) or None
            - step: int or None
            - card_id: int (optional)
        rating: int (1=Again, 2=Hard, 3=Good, 4=Easy)
        
    Returns:
        dict with updated fields:
            - stability: float
            - difficulty: float
            - due: datetime
            - last_review: datetime
            - state: int
            - step: int or None
    """
    try:
        # Create Card object from current state
        card = Card(
            card_id=card_data.get('card_id'),
            state=card_data.get('state') if card_data.get('state') is not None else 1,  # Default to Learning
            step=card_data.get('step'),
            stability=card_data.get('stability'),
            difficulty=card_data.get('difficulty'),
            due=card_data.get('due') or datetime.now(),
            last_review=card_data.get('last_review')
        )
        
        # Review the card with the given rating
        rating_enum = rating_to_fsrs_rating(rating)
        reviewed_card, review_log = scheduler.review_card(card, rating_enum)
        
        # Return updated fields
        return {
            'stability': reviewed_card.stability,
            'difficulty': reviewed_card.difficulty,
            'due': reviewed_card.due,
            'last_review': reviewed_card.last_review,
            'state': reviewed_card.state.value,
            'step': reviewed_card.step
        }
    except Exception as e:
        logger.error(f"FSRS update failed: {e}")
        # Fallback to simple interval calculation if FSRS fails
        return _fallback_update(card_data, rating)

def _fallback_update(card_data: dict, rating: int) -> dict:
    """Fallback to simple interval-based update if FSRS fails."""
    # Simple fallback: adjust interval based on rating
    interval_days = card_data.get('interval_days', 1)
    if rating >= 3:  # Good or Easy
        interval_days = max(1, round(interval_days * 1.2))
    else:  # Again or Hard
        interval_days = 1
    
    next_review = datetime.utcnow() + timedelta(days=interval_days)
    
    return {
        'stability': card_data.get('stability'),
        'difficulty': card_data.get('difficulty'),
        'due': next_review,
        'last_review': datetime.utcnow(),
        'state': card_data.get('state', 1),
        'step': card_data.get('step'),
        'interval_days': interval_days  # Keep for backward compatibility
    }

def initialize_new_card() -> dict:
    """Initialize a new card for FSRS."""
    # New cards start in Learning state with step 0
    now = datetime.utcnow()
    # Generate card_id similar to how FSRS does it (epoch milliseconds)
    card_id = int(now.timestamp() * 1000)
    # wait 1ms to prevent potential card_id collision on next Card creation
    time.sleep(0.001)
    
    return {
        'stability': None,
        'difficulty': None,
        'due': now,
        'last_review': None,
        'state': 1,  # State.Learning
        'step': 0,
        'interval_days': 0,  # For backward compatibility
        'card_id': card_id
    }