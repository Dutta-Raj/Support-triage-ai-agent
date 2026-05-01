import google.generativeai as genai
import pandas as pd
from tqdm import tqdm
import time

# REPLACE WITH YOUR ACTUAL GEMINI API KEY
GEMINI_API_KEY = "AIzaSyBRBass7Rkqlx5e7R0kw2uJXcJJR3wQZw4"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

print('='*60)
print('Support Triage Agent - Google Gemini')
print('='*60)

# Load support tickets
df = pd.read_csv('support_tickets/support_tickets.csv')
print(f'Processing {len(df)} tickets...')

def detect_domain(issue, subject, company_hint):
    if company_hint and company_hint != 'None':
        return company_hint
    text = (issue + ' ' + subject).lower()
    if 'hackerrank' in text or 'test' in text or 'assessment' in text:
        return 'HackerRank'
    if 'claude' in text or 'anthropic' in text or 'api' in text:
        return 'Claude'
    if 'visa' in text or 'card' in text or 'payment' in text:
        return 'Visa'
    return 'mixed'

def assess_risk(issue):
    text = issue.lower()
    if 'stolen' in text or 'fraud' in text or 'identity theft' in text:
        return 'critical'
    if 'security vulnerability' in text or 'unauthorized' in text:
        return 'critical'
    if 'billing' in text or 'dispute' in text or 'refund' in text:
        return 'high'
    if 'charge' in text or 'subscription' in text or 'locked' in text:
        return 'high'
    if 'delete' in text or 'remove' in text:
        return 'high'
    return 'low'

def get_request_type(issue, subject):
    text = (issue + ' ' + subject).lower()
    if 'movie' in text or 'actor' in text or 'iron man' in text:
        return 'invalid'
    if 'thank you' in text or 'happy to help' in text:
        return 'invalid'
    if 'not working' in text or 'broken' in text or 'error' in text:
        return 'bug'
    if 'failing' in text or 'down' in text or 'crash' in text:
        return 'bug'
    return 'product_issue'

def get_product_area(issue, domain):
    text = issue.lower()
    if domain == 'HackerRank':
        if 'test' in text:
            return 'Tests & Assessments'
        if 'interview' in text:
            return 'Interviews'
        if 'candidate' in text:
            return 'Candidate Management'
        return 'General Support'
    elif domain == 'Claude':
        if 'account' in text or 'billing' in text:
            return 'Account & Billing'
        if 'conversation' in text or 'chat' in text:
            return 'Conversation Management'
        return 'General Support'
    elif domain == 'Visa':
        if 'card' in text:
            return 'Card Services'
        if 'fraud' in text or 'stolen' in text:
            return 'Fraud & Security'
        if 'dispute' in text or 'charge' in text:
            return 'Dispute Resolution'
        return 'General Support'
    return 'General Support'

results = []

for index, row in tqdm(df.iterrows(), total=len(df)):
    issue = row['Issue']
    subject = row['Subject'] if pd.notna(row['Subject']) else ''
    company = row['Company'] if pd.notna(row['Company']) else None
    
    domain = detect_domain(issue, subject, company)
    risk = assess_risk(issue)
    request_type = get_request_type(issue, subject)
    product_area = get_product_area(issue, domain)
    
    # Decide status based on risk
    if risk in ['critical', 'high']:
        status = 'escalated'
        justification = f'{risk.capitalize()} risk - requires human handling'
        response = f"I'm escalating this to a human support agent. This appears to be a {risk} risk issue. Our team will contact you shortly."
    elif request_type == 'invalid':
        status = 'replied'
        justification = 'Invalid or out-of-scope request'
        response = "I'm sorry, this is out of scope from my capabilities. Please contact official support channels for assistance."
    else:
        status = 'replied'
        justification = 'Standard support query - generating response'
        # Generate response using Gemini
        prompt = f"You are a helpful customer support agent for {domain}. User question: {issue}. Provide a professional, helpful response in 2-4 sentences."
        try:
            gemini_response = model.generate_content(prompt)
            response = gemini_response.text.strip()
        except Exception as e:
            response = f"Thank you for contacting {domain} support. Our team will assist you shortly."
    
    results.append({
        'issue': issue,
        'subject': subject,
        'company': company if company else '',
        'response': response,
        'product_area': product_area,
        'status': status,
        'request_type': request_type,
        'justification': justification
    })
    
    # Small delay to avoid rate limits
    time.sleep(0.2)

# Save results
output_df = pd.DataFrame(results)
output_df.to_csv('support_tickets/output.csv', index=False)

print(f'\n✅ Done! Processed {len(results)} tickets.')
print(f'Output saved to: support_tickets/output.csv')
