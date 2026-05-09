import json
import logging
from openai import OpenAI
from utils.prompts import CLASSIFIER_PROMPT

logger = logging.getLogger(__name__)

class ClassifierAgent:
    def __init__(self, api_key):
        import os
        base_url = os.getenv("OLLAMA_BASE_URL") # Will be None if using real OpenAI
        self.model = os.getenv("OLLAMA_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def classify(self, ticket):
        """Classifies the ticket using AI."""
        logger.info(f"Classifying ticket #{ticket['id']}...")
        
        prompt = CLASSIFIER_PROMPT.format(
            subject=ticket['subject'],
            message=ticket['message']
        )

        try:
            # Note: Ollama supports response_format="json" in newer versions
            # If using an older Ollama, we might need to be careful here
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.debug(f"Classification result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in Classification Agent: {e}")
            # Fallback
            return {
                "category": "simple_question",
                "priority": "P3",
                "escalate": False
            }
