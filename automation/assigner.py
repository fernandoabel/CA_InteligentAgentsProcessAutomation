import pandas as pd

from automation.priority import priority_weights

def assign_ticket(open_tickets: pd.DataFrame, assignees: pd.DataFrame) -> str:
    """
    Assigns the next ticket to the assignee with the most capacity based on current workload.

    Parameters:
        open_tickets: The current DataFrame of all tickets.
        assignees: DataFrame of available assignees with 'name' column.

    Returns:
        str: Name of the selected assignee.
    """
    # Initialize workloads
    workload = {row['name']: 0 for _, row in assignees.iterrows()}

    # Calculate workload from existing tickets
    for _, row in open_tickets.iterrows():
        assignee = row.get("assignee")
        priority = row.get("priority", "Medium")
        if assignee in workload:
            workload[assignee] += priority_weights.get(priority, 2)

    # Select assignee with the lowest current workload
    chosen = min(workload, key=workload.get)

    return chosen