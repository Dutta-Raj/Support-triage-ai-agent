import google.generativeai as genai 
import pandas as pd 
from tqdm import tqdm 
 
# Configure Gemini with your free API key 
# Get your key from: https://aistudio.google.com/app/apikey 
genai.configure(api_key='YOUR_GEMINI_API_KEY') 
model = genai.GenerativeModel('gemini-1.5-flash') 
 
def classify_ticket(issue, subject, company_hint): 
    if company_hint and company_hint != 'None': 
        domain = company_hint 
    else: 
        issue_lower = issue.lower() 
        if 'hackerrank' in issue_lower or 'test' in issue_lower: 
            domain = 'HackerRank' 
        elif 'claude' in issue_lower: 
            domain = 'Claude' 
        elif 'visa' in issue_lower or 'card' in issue_lower: 
            domain = 'Visa' 
        else: 
            domain = 'mixed' 
    return domain 
 
print('='*60) 
print('Support Triage Agent - Gemini Version') 
print('='*60) 
 
df = pd.read_csv('support_tickets/support_tickets.csv') 
print(f'Processing {len(df)} tickets...') 
 
results = [] 
for _, row in tqdm(df.iterrows(), total=len(df)): 
    issue = row['Issue'] 
    subject = row['Subject'] if pd.notna(row['Subject']) else '' 
    company = row['Company'] if pd.notna(row['Company']) else None 
 
    domain = classify_ticket(issue, subject, company) 
 
    # Check if should escalate 
    issue_lower = issue.lower() 
    if any(x in issue_lower for x in ['stolen', 'fraud', 'identity theft', 'security vulnerability']): 
        decision = 'escalated' 
        justification = 'Critical security issue' 
        response = "I'm escalating this to a human support agent immediately. This appears to be a security-related issue." 
    elif any(x in issue_lower for x in ['billing', 'dispute', 'refund', 'charge', 'subscription']): 
        decision = 'escalated' 
        justification = 'Billing issue requires human review' 
        response = "I'm escalating this to our billing team. They will review your case and respond within 24 hours." 
    else: 
        decision = 'replied' 
        justification = 'Standard support query' 
        # Generate response with Gemini 
        prompt = f"You are a support agent for {domain}. Answer this user question helpfully: {issue}" 
        try: 
            gemini_response = model.generate_content(prompt) 
            response = gemini_response.text 
        except: 
            response = "Thank you for reaching out. Our team will assist you shortly." 
 
    results.append({ 
        'issue': issue, 
        'subject': subject, 
        'company': company if company else '', 
        'response': response, 
        'product_area': 'General Support', 
        'status': decision, 
        'request_type': 'product_issue', 
        'justification': justification 
    }) 
 
output_df = pd.DataFrame(results) 
output_df.to_csv('support_tickets/output.csv', index=False) 
print('\n? Done! Output saved to support_tickets/output.csv') 
