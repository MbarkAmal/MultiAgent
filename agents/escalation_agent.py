import logging
from openai import OpenAI
from utils.prompts import ESCALATION_SUMMARY_PROMPT
from utils.google_sheets import GoogleSheetsHandler

logger = logging.getLogger(__name__)

class EscalationAgent:
    def __init__(self, api_key, sheets_handler):
        import os
        base_url = os.getenv("OLLAMA_BASE_URL")
        self.model = os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.sheets_handler = sheets_handler

    def escalate(self, ticket, classification):
        """Summarizes and escalates the ticket."""
        logger.info(f"Escalating ticket #{ticket['id']}...")

        summary = self._generate_summary(ticket)
        
        escalation_data = {
            "id": ticket['id'],
            "subject": ticket['subject'],
            "summary": summary,
            "priority": classification['priority'],
            "category": classification['category']
        }

        # Send to Google Sheets
        success = self.sheets_handler.append_ticket(escalation_data)
        
        if success:
            logger.info(f"Ticket #{ticket['id']} successfully escalated.")
        else:
            logger.warning(f"Escalation for ticket #{ticket['id']} failed or Sheets disabled.")
            
        return summary

    def _generate_summary(self, ticket):
        """Generates a concise summary for escalation."""
        prompt = ESCALATION_SUMMARY_PROMPT.format(
            subject=ticket['subject'],
            message=ticket['message']
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Manual review required: High priority/sensitive issue."
