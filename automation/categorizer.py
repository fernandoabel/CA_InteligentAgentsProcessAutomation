# Define basic keyword-driven category prediction logic
def predict_category(summary, description):
    text = f"{summary} {description}".lower()
    if any(word in text for word in ['application', 'error', 'exception']):
        return 'Software Issue'
    if any(word in text for word in ["vpn", "network", "connection timeout"]):
        return "Network Issue"
    elif any(word in text for word in ["printer", "keyboard", "mouse", "monitor", "hardware"]):
        return "Hardware"
    elif any(word in text for word in ["software", "install", "update", "failure"]):
        return "Software"
    elif any(word in text for word in ["access", "admin", "privileges", "permission"]):
        return "Access Management"
    elif any(word in text for word in ["password", "locked", "login", "authentication"]):
        return "Security"
    elif any(word in text for word in ["slow", "performance", "cpu", "overheating"]):
        return "System Performance"
    elif any(word in text for word in ["email", "outlook", "missing email"]):
        return "Email"
    elif any(word in text for word in ["print", "printing"]):
        return "Printing"
    elif any(word in text for word in ["monitoring", "bsod", "error"]):
        return "Monitoring"
    else:
        return "User Support"