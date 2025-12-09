from typing import Optional

OBJECTIVE_SCORE_PER_QUESTION = 10
SUBJECTIVE_SCORE_PER_QUESTION = 20


def resolve_score(question_type: str, score_value: Optional[int]) -> int:
    if question_type == "subjective":
        return SUBJECTIVE_SCORE_PER_QUESTION
    return OBJECTIVE_SCORE_PER_QUESTION
