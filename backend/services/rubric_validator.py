
import math


def validate_rubric(rubric):
    # Rubric must be a non-empty dictionary
    if not isinstance(rubric, dict) or not rubric:
        raise ValueError("Rubric must be a non-empty dictionary.")

    total_weight = 0

    for criterion, details in rubric.items():

        # Each criterion must have structured details
        if not isinstance(details, dict):
            raise ValueError(
                f"{criterion}: Rubric details must be a dictionary."
            )

        # Check required fields
        required_fields = {"weight", "type", "justification"}

        if not required_fields.issubset(details):
            raise ValueError(
                f"{criterion}: Missing required rubric fields."
            )

        weight = details["weight"]

        # Validate weight
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or weight <= 0
        ):
            raise ValueError(
                f"{criterion}: Weight must be a positive number."
            )

        # Validate criterion type
        if details["type"] not in ("must_have", "preferred"):
            raise ValueError(
                f"{criterion}: Invalid criterion type."
            )

        # Validate justification
        justification = details["justification"]

        if (
            not isinstance(justification, str)
            or not justification.strip()
        ):
            raise ValueError(
                f"{criterion}: Justification is required."
            )

        total_weight += weight

    # Weights must total 100%
    if not math.isclose(total_weight, 100, abs_tol=0.000001):
        raise ValueError(
            f"Rubric weights must total 100%. Current total: {total_weight}%"
        )

    return True
