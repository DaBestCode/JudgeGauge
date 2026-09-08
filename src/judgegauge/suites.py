from .models import CalibrationCase, Candidate

SMOKE_SUITE: tuple[CalibrationCase, ...] = (
    CalibrationCase(
        id="arithmetic",
        prompt="Which candidate answers the arithmetic question more accurately: What is 17 * 6?",
        candidates=(
            Candidate("candidate_a", "102"),
            Candidate("candidate_b", "112"),
        ),
    ),
    CalibrationCase(
        id="factuality",
        prompt="Which candidate is more factually accurate about water at sea-level pressure?",
        candidates=(
            Candidate("candidate_a", "Pure water freezes at 0 degrees Celsius."),
            Candidate("candidate_b", "Pure water freezes at 20 degrees Celsius."),
        ),
    ),
    CalibrationCase(
        id="instruction",
        prompt="Which candidate better follows the instruction: Reply with exactly one lowercase word?",
        candidates=(
            Candidate("candidate_a", "done"),
            Candidate("candidate_b", "Done. The requested task is complete."),
        ),
    ),
)
