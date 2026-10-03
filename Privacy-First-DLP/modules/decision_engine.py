def make_decision(risk_score):
    if risk_score < 30:
        return "ALLOW"

    elif risk_score < 60:
        return "MASK"

    elif risk_score < 80:
        return "BLOCK"

    else:
        return "BLOCK"