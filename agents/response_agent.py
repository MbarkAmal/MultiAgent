import logging
from openai import OpenAI
from utils.prompts import RESPONSE_PROMPT, ESCALATION_SUMMARY_PROMPT

logger = logging.getLogger(__name__)

class ResponseAgent:
    def __init__(self, api_key):
        import os
        base_url = os.getenv("OLLAMA_BASE_URL")
        self.model = os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_response(self, ticket, classification):
        """Generates a response for non-escalated tickets."""
        logger.info(f"Generating response for ticket #{ticket['id']}...")

        prompt = RESPONSE_PROMPT.format(
            subject=ticket['subject'],
            message=ticket['message'],
            category=classification['category']
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error in Response Agent: {e}")
            return "Thank you for reaching out. We have received your request and will get back to you shortly."
