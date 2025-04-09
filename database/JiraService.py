from typing import Dict, List
from datetime import datetime, timedelta
import random

import pandas as pd

from database.EntityService import EntityService

class JiraMockService:

    def __init__(self, tickets_file: str = "database/jira_tickets.csv", users_file='database/jira_users.csv', auto_save=True):
        """Initialize the JIRA service."""
        print('Initializing Jira Service', [tickets_file, users_file])
        self.tickets_file = tickets_file
        self.users_file = users_file
        self.tickets_service = EntityService(self.tickets_file,
                                      ['ticket_id', 'summary', 'description', 'status', 'assignee', 'created_at', 'category', 'priority'],
                                             'ticket_id',
                                             'TKT')
        self.users_service = EntityService(self.users_file,
                                        ['user_id', 'name', 'email', 'role', 'phone'],
                                           'user_id',
                                           'USER')
        self.auto_save = auto_save

    def create_ticket(self, ticket: Dict) -> Dict:
        ticket = {
            'summary': ticket['summary'],
            'description': ticket['description'],
            'status': ticket['status'] if 'status' in ticket else 'Open',
            'assignee': ticket['assignee'],
            'created_at': datetime.now().isoformat(),
            'category': ticket['category'] if 'category' in ticket else None,
            'priority': ticket['priority'] if 'priority' in ticket else None,
        }
        ticket = self.tickets_service.insert(ticket)
        if self.auto_save:
            self.save()
        return ticket

    def create_user(self, user: Dict) -> Dict:
        user = {
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "phone": user['phone']
        }
        user = self.users_service.insert(user)
        if self.auto_save:
            self.save()
        return user

    def update_ticket(self, ticket_id: str, data: Dict) -> Dict:
        ticket = self.tickets_service.update(ticket_id, data)
        if self.auto_save:
            self.save()
        return ticket

    def get_all_tickets(self) -> pd.DataFrame:
        return self.tickets_service.data

    def get_all_users(self) -> pd.DataFrame:
        return self.users_service.data

    def find_ticket_by_id(self, ticket_id: str) -> Dict:
        match = self.tickets_service.data[self.tickets_service.data['ticket_id'] == ticket_id]
        return match.to_dict(orient='records')[0] if not match.empty else {}

    def find_user_by_id(self, ticket_id: str) -> Dict:
        match = self.tickets_service.data[self.tickets_service.data['user_id'] == ticket_id]
        return match.to_dict(orient='records')[0] if not match.empty else {}

    def save(self):
        """Save all tables."""
        self.tickets_service.save_changes()
        self.users_service.save_changes()

    def initializeData(self):
        # Sample data for mock ticket generation
        summaries = [
            "Unable to access intranet",
            "Outlook not syncing emails",
            "Printer not working on 3rd floor",
            "VPN connection timeout",
            "Password reset required",
            "New employee onboarding setup",
            "System slowness during login",
            "Access request for finance folder",
            "Software update failure",
            "Laptop overheating frequently",
            "Blue screen error on startup",
            "File recovery request",
            "Install antivirus software",
            "Account locked after failed attempts",
            "Cannot connect to shared drive",
            "Request for admin privileges",
            "Two-factor authentication setup",
            "Missing email from inbox",
            "Monitor not detecting input",
            "Mouse and keyboard unresponsive"
        ]

        descriptions = [
            "User reports they cannot access the internal bank portal.",
            "Emails are not syncing across desktop and mobile devices.",
            "Printer on 3rd floor throws paper jam error frequently.",
            "VPN disconnects after 5 minutes of use.",
            "User forgot their password and is locked out of their account.",
            "New employee joining on Monday requires system setup.",
            "Multiple users report slow login times in the morning.",
            "Need read-only access to finance folder for audit purposes.",
            "Update failed with error code 0x800f0831 on several machines.",
            "Laptop CPU temperatures exceed 90°C while idle.",
            "User encounters BSOD during startup with error 0x0000007B.",
            "Need help recovering accidentally deleted financial files.",
            "Antivirus software missing on workstation.",
            "User account locked due to multiple failed login attempts.",
            "Shared drive not visible under network locations.",
            "User requests temporary admin access to install software.",
            "Help needed to configure 2FA for remote login.",
            "User cannot locate important client email in inbox.",
            "Monitor screen remains black despite power supply.",
            "Mouse and keyboard are not responding after reboot."
        ]

        assignees = ["Alice", "Bob", "Charlie", "Diana", "Eric", "Fernando", "Vivek", "Paul", "Conor"]
        roles = ["Analyst", "Engineer", "QA Tester"]
        # Define some creative categories and priorities
        categories = [
            "Software Issue", "Network Issue", "Hardware", "Software", "Access Management", "Security",
            "System Performance", "User Support", "Email", "Printing", "Monitoring"
        ]
        priorities = ["Low", "Medium", "High", "Critical"]


        if len(jira.get_all_users()) == 0:
            for name in assignees:
                email = f"{name.lower()}@email.ie"
                role = random.choice(roles)
                phone = f"+1-202-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                self.create_user({
                    "name": name,
                    "email": email,
                    "role": role,
                    "phone": phone
                })

        statuses_distribution = {
            "Open": 30,
            "In Progress": 15,
            "Waiting for User": 5,
            "Resolved": 20,
            "Closed": 430  # Total should be 500
        }

        if len(jira.get_all_tickets()) == 0:
            # Generate 500+ mock tickets
            ticket_id = 1
            for status, count in statuses_distribution.items():
                for _ in range(count):
                    idx = random.randint(0, len(summaries) - 1)
                    ticket = {
                        'summary': summaries[idx],
                        'description': descriptions[idx],
                        'status': status,
                        'assignee': None if status == 'Open' else random.choice(assignees),
                        'category': None if status == 'Open' else random.choice(categories),
                        'priority': None if status == 'Open' else random.choice(priorities),
                    }
                    self.create_ticket(ticket)
                    ticket_id += 1


# --- Example usage ---
if __name__ == "__main__":
    jira = JiraMockService("jira_tickets.csv", "jira_users.csv")

    jira.initializeData()

    # Retrieve all
    tickets = pd.DataFrame(jira.get_all_tickets())
    print("Total Users:", len(jira.get_all_users()))
    print("Total Tickets:", len(tickets))
    print("Grouped By Status", tickets.groupby(['status']).size())
    print("Grouped By Assignee", tickets.groupby(['assignee']).size())
