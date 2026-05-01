# Responder module 
 
import os 
from openai import OpenAI 
from dotenv import load_dotenv 
 
load_dotenv() 
 
class ResponseGenerator: 
    def __init__(self, retriever): 
        self.retriever = retriever 
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) 
 
    def generate(self, issue, classification, decision, context): 
        if decision['status'] == 'escalated': 
            return f"I'm escalating this to a human support agent. {decision['reason']}" 
        if classification['request_type'] == 'invalid': 
            return "I'm sorry, this is out of scope from my capabilities." 
        return "Based on our documentation, I'm processing your request. A support representative will follow up if needed." 
