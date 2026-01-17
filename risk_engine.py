
def calculate_risk_index(sensor_data, zone):
    """
    Inputs:
    sensor_data: Dict with 'mpu' and 'motor' structures
    zone: "RED", "YELLOW", or "GREEN"
    """
    score = 0
    reasons = []

    # 1. Geospace Penalty (Hard Rule)
    if zone == "RED":
        return 100, "CRITICAL: Restricted Airspace", "DANGER"
    elif zone == "YELLOW":
        score += 30
        reasons.append("Near Airport")

    # 2. Hardware Penalty
    vib = sensor_data.get('mpu', {}).get('vibration_rms', 0)
    if vib > 0.3: # Increased threshold for G-force units
        score += 40
        reasons.append("High Vibration")
    
    rpm = sensor_data.get('motor', {}).get('rpm', 1000)
    if rpm < 400 and rpm > 0: # Check only if running
        score += 30
        reasons.append("Low Motor Efficiency")

    # Final logic
    score = min(score, 100)
    recommendation = "SAFE" if score < 40 else "CAUTION" if score < 75 else "ABORT"
    
    reason_str = ", ".join(reasons) if reasons else "Systems Nominal"
    return score, f"{recommendation}: {reason_str}", recommendation
