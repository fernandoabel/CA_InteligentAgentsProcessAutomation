import pandas as pd
import os

class EntityService:
    file_path = ''

    def __init__(self, file_path: str, columns: list[str], key: str, prefix: str):
        self.file_path = file_path
        self.key = key if key else 'ID'
        self.prefix = prefix
        self.columns = columns
        self._ensure_file_exists()
        self.data = self._load_table()
        pass

    def _ensure_file_exists(self):
        """Ensure CSV file exists with headers."""
        if not os.path.exists(self.file_path):
            pd.DataFrame(columns=self.columns).to_csv(self.file_path, index=False)

    def _load_table(self):
        """Load table from CSV into a DataFrame, ensuring proper handling of empty files."""
        df = pd.read_csv(self.file_path, delimiter=',')
        if df.empty:
            df = pd.DataFrame(columns=self.columns)
        return df

    def save_changes(self):
        """Save the current state of DataFrames back to CSV files."""
        self.data.to_csv(self.file_path, index=False)

    def _generate_ticket_id(self) -> str:
        if self.data.empty:
            return f"{self.prefix}-0001"
        last_num = self.data.shape[0] + 1
        return f"{self.prefix}-{last_num:04d}"

    def insert(self, data):
        """Insert a new record into the table."""
        if self.key not in data:
            data[self.key] = self._generate_ticket_id()
        self.data = pd.concat([self.data, pd.DataFrame([data], columns=self.columns)], ignore_index=True)
        return data

    def update(self, row_id, data):
        """Update a record in the table."""
        for col, val in data.items():
            self.data.loc[self.data[self.key] == row_id, col] = val

        return data

    def delete(self, row_id):
        """Delete a record from the table."""
        self.data = self.data[self.data[self.key] != row_id]