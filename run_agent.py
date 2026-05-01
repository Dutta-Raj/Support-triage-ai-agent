import pandas as pd 
import sys 
from tqdm import tqdm 
 
# Add code directory to path 
sys.path.insert(0, r'C:\Users\KIIT\Desktop\hackerrank-orchestrate-may26\code') 
 
from agent.classifier import TicketClassifier 
from agent.retriever import SupportRetriever 
from agent.decider import EscalationDecider 
from agent.responder import ResponseGenerator 
 
print('='*60) 
print('Support Triage Agent - HackerRank Orchestrate 2026') 
print('='*60) 
 
# Load the CSV from correct path 
df = pd.read_csv('support_tickets/support_tickets.csv') 
print(f'Processing {len(df)} tickets...') 
 
classifier = TicketClassifier() 
retriever = SupportRetriever() 
decider = EscalationDecider() 
responder = ResponseGenerator(retriever) 
 
results = [] 
for _, row in tqdm(df.iterrows(), total=len(df)): 
    issue = row['Issue'] 
    subject = row['Subject'] if pd.notna(row['Subject']) else '' 
    company = row['Company'] if pd.notna(row['Company']) else None 
 
    classification = classifier.classify(issue, subject, company) 
    context = retriever.retrieve(issue, classification['domain']) 
    decision = decider.decide(issue, classification, context) 
    response = responder.generate(issue, classification, decision, context) 
 
    results.append({ 
        'issue': issue, 
        'subject': subject, 
        'company': company if company else '', 
        'response': response, 
        'product_area': classification['product_area'], 
        'status': decision['status'], 
        'request_type': classification['request_type'], 
        'justification': decision['reason'] 
    }) 
 
output_df = pd.DataFrame(results) 
output_df.to_csv('support_tickets/output.csv', index=False) 
print(f'\n? Done! Output saved to support_tickets/output.csv') 
