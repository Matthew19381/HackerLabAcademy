"""
SM-2 spaced repetition algorithm.

Rating scale (1-4):
  1 = Didn't know (blackout)
  2 = Hard (significant effort)
  3 = Good (correct with some effort)
  4 = Easy (perfect recall)
"""
from datetime import datetime, timedelta


def sm2_update(ease_factor: float, interval_days: int, repetitions: int, rating: int) -> dict:
    """
    Apply SM-2 algorithm and return updated fields.
    rating: 1 (didn't know) | 2 (hard) | 3 (good) | 4 (easy)
    """
    if rating < 3:
        # Failed — reset to beginning
        repetitions = 0
        interval_days = 1
    else:
        if repetitions == 0:
            interval_days = 1
        elif repetitions == 1:
            interval_days = 6
        else:
            interval_days = round(interval_days * ease_factor)
        repetitions += 1

    # Update ease factor (never below 1.3)
    new_ef = ease_factor + (0.1 - (4 - rating) * (0.08 + (4 - rating) * 0.02))
    ease_factor = max(1.3, new_ef)

    next_review = datetime.utcnow() + timedelta(days=interval_days)

    return {
        "ease_factor": round(ease_factor, 2),
        "interval_days": interval_days,
        "repetitions": repetitions,
        "next_review_date": next_review,
    }
