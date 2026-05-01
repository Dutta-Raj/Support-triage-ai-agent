# Classifier module 
 
from .utils import detect_domain_from_text, assess_risk_level, classify_request_type, extract_product_area 
 
class TicketClassifier: 
    def classify(self, issue, subject, company_hint): 
        if company_hint and company_hint != 'None': 
            domain = company_hint 
        else: 
            domain = detect_domain_from_text(f"{issue} {subject}") 
        request_type = classify_request_type(issue, subject) 
        risk_level = assess_risk_level(issue, request_type) 
        product_area = extract_product_area(issue, domain) 
        return {'domain': domain, 'request_type': request_type, 'risk_level': risk_level, 'product_area': product_area} 
