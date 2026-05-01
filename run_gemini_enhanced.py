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
print('Support Triage Agent - Google Gemini (Enhanced)')
print('='*60)

# Load support tickets
df = pd.read_csv('support_tickets/support_tickets.csv')
print(f'Processing {len(df)} tickets...')

def detect_domain(issue, subject, company_hint):
    if company_hint and company_hint != 'None':
        return company_hint
    text = (issue + ' ' + subject).lower()
    if 'hackerrank' in text or 'test' in text or 'assessment' in text or 'coding' in text:
        return 'HackerRank'
    if 'claude' in text or 'anthropic' in text or 'api' in text or 'bedrock' in text:
        return 'Claude'
    if 'visa' in text or 'card' in text or 'payment' in text or 'transaction' in text:
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
        if 'certificate' in text:
            return 'Certificates'
        if 'resume' in text:
            return 'Resume Builder'
        return 'General Support'
    elif domain == 'Claude':
        if 'account' in text or 'billing' in text:
            return 'Account & Billing'
        if 'conversation' in text or 'chat' in text:
            return 'Conversation Management'
        if 'api' in text or 'bedrock' in text:
            return 'API & Console'
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

# Knowledge base for common HackerRank questions
def get_hackerrank_answer(issue):
    text = issue.lower()
    
    # Test expiration
    if 'test active' in text or 'how long' in text and 'active' in text:
        return """Tests in HackerRank remain active indefinitely unless a start and end time are set. Without these, tests do not expire automatically.

To set expiration times, specify a start and end date/time in the test settings. After expiration:
- Invited candidates cannot access the test
- The "Invite" button is disabled; no new invitations can be sent

To keep a test active indefinitely, clear the Start date & time and End date & time fields."""
    
    # Test variants
    if 'variant' in text or 'create a new test' in text:
        return """Test Variants allow you to adapt a single test to different candidate profiles (e.g., React, Angular, Vue.js developers).

Advantages of Test Variants:
- Reduces the need to manage multiple tests
- Decreases maintenance while allowing scalable personalization
- Ensures candidates are tested on relevant content

Note: A test must have at least two variants to function."""
    
    # Extra time for candidates
    if 'extra time' in text or 'add time' in text or 'time accommodation' in text:
        return """To add extra time for a candidate:

1. Go to the Tests tab
2. Select the test you want to modify
3. Go to the Candidates tab
4. Select the checkbox next to the candidate(s)
5. Click More > Add Time Accommodation
6. Enter the accommodation percentage in multiples of five
7. Click Save

Time accommodation can be added before or after the invite has been sent."""
    
    # Delete account
    if 'delete my account' in text:
        return """To delete your HackerRank account:

1. If using Google login, first set a password via "Forgot your password?"
2. Log in to your account
3. Click your profile icon → Settings
4. Scroll to Delete Accounts section
5. Click Delete Account and follow prompts

Deleting your account will permanently remove all data and cannot be undone."""
    
    # Remove user/interviewer
    if 'remove' in text and ('interviewer' in text or 'user' in text or 'employee' in text):
        return """To remove a user from your HackerRank account:

1. Go to Settings → Teams Management
2. Find the user you want to remove
3. Click on the three dots next to their name
4. Select "Remove" or "Deactivate"
5. Confirm the action

Note: Only Account Admins and Team Admins can remove users."""
    
    # Test not working
    if 'not working' in text or 'blocker' in text or 'compatible check' in text:
        return """If you're experiencing technical issues with a HackerRank test:

1. Try using a supported browser (Chrome, Firefox, Edge)
2. Clear your browser cache and cookies
3. Disable browser extensions
4. Check your internet connection
5. Ensure Zoom is properly installed if required

If issues persist, please contact support with details about the error message."""
    
    # Certificate name update
    if 'certificate' in text and 'name' in text:
        return """To update your name on a HackerRank certificate:

1. Go to your account Settings
2. Update your profile name
3. The certificate will automatically reflect the updated name

For certificates already issued, you may need to retake the assessment or contact support."""
    
    return None

# Knowledge base for Claude questions
def get_claude_answer(issue):
    text = issue.lower()
    
    # Delete conversation
    if 'delete' in text and ('conversation' in text or 'chat' in text):
        return """To delete an individual conversation in Claude:

1. Navigate to the conversation you want to delete
2. Click on the name of the conversation at the top of the screen
3. Select "Delete" from the options that appear

This will permanently remove the conversation."""
    
    # Data usage
    if 'data' in text and ('use' in text or 'improve' in text):
        return """When you allow Claude to use your data to improve models:

- Your data is used for model training and improvement
- Data is anonymized and handled according to Anthropic's privacy policy
- Retention periods vary by data type
- You can request data export or deletion at any time via your account settings

For specific retention periods, please review Anthropic's Privacy Policy or contact support."""
    
    # API issues
    if 'api' in text or 'bedrock' in text or 'failing' in text:
        return """If you're experiencing issues with Claude API or AWS Bedrock:

1. Check your API key is valid and has not expired
2. Verify your rate limits and quota
3. Check AWS Bedrock service status
4. Review error messages for specific guidance
5. Ensure you're using the correct model endpoints

For immediate assistance, contact support with your error logs."""
    
    # Not responding
    if 'not responding' in text or 'stopped working' in text:
        return """If Claude is not responding:

1. Refresh the page or restart the application
2. Check your internet connection
3. Clear browser cache and cookies
4. Try incognito/private mode
5. Check system status at status.anthropic.com

If issues persist, please contact Claude support."""
    
    return None

# Knowledge base for Visa questions
def get_visa_answer(issue):
    text = issue.lower()
    
    # Dispute charge
    if 'dispute' in text or 'charge' in text:
        return """To dispute a Visa charge:

1. Contact the merchant first to resolve the issue
2. If unresolved, call your card issuer (the bank that issued your Visa card)
3. Provide transaction details, amount, and date
4. Explain why you're disputing the charge
5. The issuer will investigate and may issue a temporary credit

For Visa India cardholders, call the number on the back of your card or 000-800-100-1219 for assistance."""
    
    # Lost/stolen card
    if 'stolen' in text or 'lost' in text:
        return """If your Visa card is lost or stolen:

1. Call your card issuer immediately to block the card
2. For Visa India: 000-800-100-1219
3. From outside India: +1 303 967 1090 (24/7 Global Customer Assistance)
4. Your issuer will block the card within ~30 minutes
5. They can arrange emergency cash and a replacement card

Have your card number and recent transactions ready when you call."""
    
    # Fraud
    if 'fraud' in text or 'unauthorized' in text:
        return """If you suspect fraudulent activity on your Visa card:

1. IMMEDIATELY call your card issuer's fraud department
2. For Visa India: 000-800-100-1219
3. Review recent transactions and identify unauthorized charges
4. Your issuer will investigate and typically provide provisional credit
5. File a police report if required by your issuer

Do not share OTPs, PINs, or card details with anyone contacting you."""
    
    # Minimum spend
    if 'minimum' in text or 'spend' in text:
        return """Merchants may set minimum transaction amounts for card payments due to processing fees. Visa does not set these minimums.

While Visa's rules generally prohibit minimums, some merchants may still require them. Your options:
1. Ask the merchant to waive the minimum
2. Use an alternative payment method
3. Report the merchant to Visa via your card issuer

Contact your card issuer for specific guidance on merchant minimums."""
    
    # Blocked card
    if 'blocked' in text or 'bloqu' in text:
        return """If your Visa card is blocked:

1. Call your card issuer immediately to understand why
2. For Visa India: 000-800-100-1219
3. Common reasons: suspicious activity, incorrect PIN, exceeded limits
4. Your issuer can usually unblock it after verifying your identity
5. If traveling, inform your bank about travel plans before you go

For international travel, always carry a backup payment method."""
    
    return None

# Main processing
results = []

for index, row in tqdm(df.iterrows(), total=len(df)):
    issue = row['Issue']
    subject = row['Subject'] if pd.notna(row['Subject']) else ''
    company = row['Company'] if pd.notna(row['Company']) else None
    
    domain = detect_domain(issue, subject, company)
    risk = assess_risk(issue)
    request_type = get_request_type(issue, subject)
    product_area = get_product_area(issue, domain)
    
    # Check if critical/high risk - escalate
    if risk in ['critical', 'high']:
        status = 'escalated'
        justification = f'{risk.capitalize()} risk - requires human handling'
        response = f"I'm escalating this to a human support agent. This appears to be a {risk} risk issue. Our team will contact you shortly."
    
    # Check if invalid
    elif request_type == 'invalid':
        status = 'replied'
        justification = 'Invalid or out-of-scope request'
        response = "I'm sorry, this is out of scope from my capabilities. Please contact official support channels for assistance."
    
    else:
        # Try to get specific answer from knowledge base
        specific_answer = None
        if domain == 'HackerRank':
            specific_answer = get_hackerrank_answer(issue)
        elif domain == 'Claude':
            specific_answer = get_claude_answer(issue)
        elif domain == 'Visa':
            specific_answer = get_visa_answer(issue)
        
        if specific_answer:
            status = 'replied'
            justification = f'Found specific answer in knowledge base for {domain}'
            response = specific_answer
        else:
            # Use Gemini for custom answer
            status = 'replied'
            justification = 'Using AI to generate custom response'
            prompt = f"""You are a helpful customer support agent for {domain}. 
            
User question: {issue}

Provide a specific, helpful response with step-by-step instructions if applicable. 
Keep it concise and professional (3-5 sentences).
Base your answer on typical support knowledge for {domain}.
If you don't know, suggest contacting support."""
            
            try:
                gemini_response = model.generate_content(prompt)
                response = gemini_response.text.strip()
            except Exception as e:
                response = f"Thank you for contacting {domain} support. Please visit our help center at support.{domain.lower()}.com for assistance."
    
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
    
    time.sleep(0.2)  # Avoid rate limits

# Save results
output_df = pd.DataFrame(results)
output_df.to_csv('support_tickets/output.csv', index=False)

print(f'\n✅ Enhanced output saved to: support_tickets/output.csv')
print(f'   - {len([r for r in results if r["status"] == "escalated"])} escalated')
print(f'   - {len([r for r in results if r["status"] == "replied"])} replied')
