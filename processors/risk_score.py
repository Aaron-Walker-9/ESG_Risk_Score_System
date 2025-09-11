def calculate_risk_score(row):
    risk = 0
    # Environment
    if row["Environment"] != "none" and row["Sentiment"] == "NEGATIVE":
        risk += row["Env_score"] * row["Senti_score"]
    # Social
    if row["Social"] != "none" and row["Sentiment"] == "NEGATIVE":
        risk += row["Social_score"] * row["Senti_score"]
    # Governance
    if row["Government"] != "none" and row["Sentiment"] == "NEGATIVE":
        risk += row["Gov_score"] * row["Senti_score"]
    return risk