def predict_priority(summary: str, description: str, category: str = None) -> str:
    # Priority mapping based on known categories
    category_priority_map = {
        "Software Issue": "Critical",
        "Security": "Critical",
        "Network Issue": "High",
        "Access Management": "High",
        "Monitoring": "High",
        "System Performance": "Medium",
        "Software": "Medium",
        "Hardware": "Medium",
        "Email": "Medium",
        "Printing": "Low",
        "User Support": "Low"
    }

    if category and category in category_priority_map:
        return category_priority_map[category]

    # Fallback keyword-based rule if category is unknown
    text = f"{summary} {description}".lower()

    if any(keyword in text for keyword in ["locked", "unauthorized", "authentication", "security"]):
        return "Critical"
    elif any(keyword in text for keyword in ["vpn", "network", "access denied", "timeout"]):
        return "High"
    elif any(keyword in text for keyword in ["slow", "performance", "update", "failure", "error"]):
        return "Medium"
    elif any(keyword in text for keyword in ["printer", "mouse", "keyboard", "request", "support"]):
        return "Low"
    else:
        return "Medium"  # Default fallback
