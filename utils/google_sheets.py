import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os

logger = logging.getLogger(__name__)

class GoogleSheetsHandler:
    def __init__(self, credentials_file, sheet_name):
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.client = self._authenticate()

    def _authenticate(self):
        """Authenticates with Google Sheets API."""
        if not os.path.exists(self.credentials_file):
            logger.warning(f"Credentials file {self.credentials_file} not found. Google Sheets integration will be disabled.")
            return None
        
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        return gspread.authorize(creds)

    def append_ticket(self, ticket_data):
        """Appends a row to the spreadsheet."""
        if not self.client:
            logger.error("Cannot append ticket: Not authenticated.")
            return False

        try:
            sheet = self.client.open(self.sheet_name).sheet1
            # Columns: Ticket ID, Subject, Summary, Priority, Category
            row = [
                ticket_data.get('id'),
                ticket_data.get('subject'),
                ticket_data.get('summary'),
                ticket_data.get('priority'),
                ticket_data.get('category')
            ]
            sheet.append_row(row)
            logger.info(f"Successfully escalated ticket #{ticket_data.get('id')} to Google Sheets.")
            return True
        except Exception as e:
            logger.error(f"Error appending to Google Sheets: {e}")
            return False
