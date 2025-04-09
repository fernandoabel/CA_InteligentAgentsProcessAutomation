import os
import pandas as pd
from automation.priority import priority_weights

def summary_tickets_email(tickets: pd.DataFrame):
    # Assigned Pending Tickets
    open_tickets = tickets[
        (tickets['status'].isin(['Open', 'In Progress', 'Waiting for User'])) &
        ~tickets['category'].isnull() &
        ~tickets['priority'].isnull() &
        ~tickets['assignee'].isnull()
        ]
    df = open_tickets.copy()
    df["priority_weight"] = df["priority"].map(priority_weights)
    # Sort Descending by Assignee and Priority Weight
    df.sort_values(by=["assignee", "priority_weight"], ascending=False, inplace=True)

    # Group by assignee
    grouped = df.groupby("assignee")

    output_dir = ".\\notifications\\ticketsSummary"
    os.makedirs(output_dir, exist_ok=True)

    # Generate email bodies per assignee
    for assignee, group in grouped:
        filename = os.path.join(output_dir, f"{assignee}.html")
        generate_email_html(assignee, group, filename)


def generate_email_html(assignee, tickets_df: pd.DataFrame, output_path="ticket_summary.html") -> str:
    style = None

    if tickets_df.empty:
        html_body = "<p>No open tickets to display.</p>"
    else:
        df = tickets_df[['ticket_id', 'summary', 'status', 'assignee', 'category', 'priority']].copy()

        style = """
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            h2 {
                color: #333;
            }
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th {
                background-color: #f2f2f2;
                color: #333;
            }
            td, th {
                border: 1px solid #ddd;
                text-align: left;
                padding: 8px;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
        """

        html_table = df.to_html(index=False, escape=False)
        html_body = f"""
        <h2>Open Ticket Summary</h2>
        <p>Hi {assignee},</p>
        <p>Here is a summary of your currently assigned <b>Open</b> tickets, sorted by priority:</p>
        {html_table}
        
        <p>Please address these as soon as possible based on urgency.</p>
        
        <p>
        Regards, <br>
        IT Support Team
        </p>
        """

    html = f"""
    <html>
        <head>{style}</head>
        <body>{html_body}</body>
    </html>
    """

    # Save to HTML file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html

if __name__ == "__main__":
    pass