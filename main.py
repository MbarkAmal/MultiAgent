import os
import json
import logging
import time
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Agent Imports
from agents.classifier_agent import ClassifierAgent
from agents.response_agent import ResponseAgent
from agents.escalation_agent import EscalationAgent
from utils.google_sheets import GoogleSheetsHandler

# Initialize Colorama
init(autoreset=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("support_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MainPipeline")

def load_tickets(file_path):
    """Loads tickets from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Tickets file not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading tickets: {e}")
        return []

def save_responses(responses, file_path):
    """Saves generated responses to a JSON File."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(responses, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved {len(responses)} responses to {file_path}")
    except Exception as e:
        logger.error(f"Error saving responses: {e}")

def run_pipeline():
    # 1. Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    sheet_name = os.getenv("GOOGLE_SHEET_NAME", "CustomerSupportEscalations")
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

    if not api_key:
        print(f"{Fore.RED}CRITICAL ERROR: OPENAI_API_KEY not found in .env file.{Style.RESET_ALL}")
        return

    # 2. Initialize Agents and Utils
    classifier = ClassifierAgent(api_key)
    responder = ResponseAgent(api_key)
    sheets_handler = GoogleSheetsHandler(creds_file, sheet_name)
    escalator = EscalationAgent(api_key, sheets_handler)

    # 3. Load Tickets
    tickets_path = os.path.join("data", "tickets.json")
    tickets = load_tickets(tickets_path)
    
    if not tickets:
        print(f"{Fore.YELLOW}No tickets to process.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}STARTING CUSTOMER SUPPORT AGENT PIPELINE")
    print(f"{Fore.CYAN}{'='*50}\n")

    processed_results = []

    # 4. Process Tickets
    for ticket in tickets:
        print(f"{Fore.WHITE}Processing Ticket #{ticket['id']} - {ticket['subject']}...")
        
        try:
            # Step 1: Classification
            classification = classifier.classify(ticket)
            
            result_entry = {
                "ticket_id": ticket['id'],
                "subject": ticket['subject'],
                "classification": classification,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            # Step 2: Branching Logic
            if classification.get('escalate'):
                print(f"  {Fore.MAGENTA}>> Escalating ticket...")
                summary = escalator.escalate(ticket, classification)
                result_entry["status"] = "Escalated"
                result_entry["escalation_summary"] = summary
            else:
                print(f"  {Fore.GREEN}>> Generating response...")
                response = responder.generate_response(ticket, classification)
                result_entry["status"] = "Responded"
                result_entry["response"] = response
                print(f"  {Fore.BLUE}Response: {response[:50]}...")

            processed_results.append(result_entry)
            
            # Anti-rate limit delay
            time.sleep(1)

        except Exception as e:
            logger.error(f"Failed to process ticket #{ticket['id']}: {e}")
            print(f"  {Fore.RED}!! Error processing ticket.")

    # 5. Save Results
    responses_path = os.path.join("data", "responses.json")
    save_responses(processed_results, responses_path)

    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}PIPELINE COMPLETED SUCCESSFULLY")
    print(f"{Fore.CYAN}{'='*50}\n")

if __name__ == "__main__":
    run_pipeline()
