# similarity threshold (tune if needed)
SIMILARITY_THRESHOLD = 1.5


def is_relevant(distance):
    """
    Check if retrieved result is relevant
    Lower distance = better match
    """
    return float(distance) <= SIMILARITY_THRESHOLD


def guardrail_response(distances):
    """
    Apply guardrail logic safely for numpy arrays
    """
    try:
        # 🔥 FIX 1: handle empty safely (no 'not distances')
        if distances is None or len(distances) == 0:
            return False, "❌ Answer not found in selected documents"

        # 🔥 FIX 2: extract scalar safely
        best_distance = float(distances[0][0])

        # 🔥 FIX 3: compare properly
        if best_distance > SIMILARITY_THRESHOLD:
            return False, "❌ Answer not found in selected documents"

        return True, None

    except Exception as e:
        print("Guardrail Error:", e)
        return False, "❌ Guardrail processing failed"