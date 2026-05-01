# Utility functions 
 
def detect_domain_from_text(text): 
    text_lower = text.lower() 
    if 'hackerrank' in text_lower or 'test' in text_lower or 'candidate' in text_lower: 
        return 'HackerRank' 
    if 'claude' in text_lower or 'anthropic' in text_lower or 'api' in text_lower: 
        return 'Claude' 
    if 'visa' in text_lower or 'card' in text_lower or 'payment' in text_lower: 
        return 'Visa' 
    return 'mixed' 
 
def assess_risk_level(issue, request_type): 
    issue_lower = issue.lower() 
    if any(x in issue_lower for x in ['stolen','fraud','identity theft','security vulnerability']): 
        return 'critical' 
    if any(x in issue_lower for x in ['billing','dispute','refund','charge','subscription','locked','delete']): 
        return 'high' 
    return 'low' 
 
def classify_request_type(issue, subject): 
    combined = f"{issue} {subject}".lower() 
    if any(x in combined for x in ['movie','actor','iron man','thank you','happy to help']): 
        return 'invalid' 
    if any(x in combined for x in ['not working','broken','error','failing','down','crash','bug']): 
        return 'bug' 
    return 'product_issue' 
 
def extract_product_area(issue, domain): 
    issue_lower = issue.lower() 
    if domain == 'HackerRank': 
        if 'interview' in issue_lower: return 'Interviews' 
        return 'General Support' 
    if domain == 'Claude': 
        if 'account' in issue_lower: return 'Account Management' 
        return 'General Support' 
    if domain == 'Visa': 
        if 'card' in issue_lower: return 'Card Services' 
        return 'General Support' 
    return 'General Support' 
