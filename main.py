import numpy as np
import pandas as pd
from threading import Thread, Event, Lock
import time

from automation import predict_category, predict_priority, assign_ticket
from database import JiraMockService
from notifications.summary_email import summary_tickets_email


class TicketWatcher:
    def __init__(self, interval: int = 5, notification_mail_interval=10):
        self.jira = JiraMockService()
        self.interval = interval
        self.notification_mail_interval = notification_mail_interval
        self._stop_event = Event()
        self._thread = Thread(target=self._watch_loop)
        self._thread2 = Thread(target=self._notify_loop)
        self.lock = Lock()

    def start(self):
        print("TicketWatcher started.")
        self._thread.start()
        self._thread2.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()
        self._thread2.join()
        print("TicketWatcher stopped.")

    def _watch_loop(self):
        """
        Watch for every ticket in status Open, that requires being categorized, prioritized and assigned
        """
        while not self._stop_event.is_set():
            with self.lock:
                users = self.jira.get_all_users()
                tickets = self.jira.get_all_tickets()

                pending_tickets = tickets[
                    (tickets['status'] == 'Open') &
                    (tickets['category'].isnull() | tickets['priority'].isnull() | tickets['assignee'].isnull())
                ]

                if pending_tickets.empty:
                    print(f"No ticket(s) found to be categorized, prioritized or assigned.")
                else:
                    for idx in pending_tickets.index:
                        ticket = pending_tickets.loc[idx].to_dict()

                        # Assign category, priority and assignee
                        if ticket['category'] is None or np.isnan(ticket['category']):
                            ticket['category'] = categorizeTicket(ticket)
                        if ticket['priority'] is None or np.isnan(ticket['priority']):
                            ticket['priority'] = prioritizeTicket(ticket)
                        if ticket['assignee'] is None or np.isnan(ticket['assignee']):
                            tickets_being_worked = tickets[
                                (tickets['status'].isin(['Open', 'In Progress', 'Waiting for User'])) &
                                (~tickets['assignee'].isnull())
                                ]
                            ticket['assignee'] = assignTicket(tickets_being_worked, users)

                        ticket_id = ticket['ticket_id']
                        ticket = self.jira.update_ticket(ticket_id, ticket)
                        # tickets.loc[tickets['ticket_id'] == ticket['ticket_id'], :] = pd.DataFrame([ticket])

                        print(f"Processed ticket {ticket_id}, assigned to {ticket['assignee']}")
                    print(f"Processed {len(pending_tickets)} ticket(s).")


            print(f"Sleeping for {self.interval} seconds.")
            time.sleep(self.interval)

    def _notify_loop(self):
        """
        Sends Summary of Pending Tickets to every user in HTML format
        """
        while not self._stop_event.is_set():
            with self.lock:
                tickets = pd.DataFrame(self.jira.get_all_tickets())
                summary_tickets_email(tickets)
                print(f"Notification sent to assignees")
                time.sleep(self.notification_mail_interval)


def categorizeTicket(ticket: dict) -> str:
    return predict_category(ticket['summary'], ticket['description'])

def prioritizeTicket(ticket: dict) -> str:
    return predict_priority(ticket['summary'], ticket['description'], ticket['category'])

def assignTicket(tickets: pd.DataFrame, users: pd.DataFrame) -> str:
    return assign_ticket(tickets, users)

# Usage Example
if __name__ == "__main__":

    # Process tickets every 10 seconds
    watcher = TicketWatcher(interval=10, notification_mail_interval=30)
    watcher.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
