# Decider module 
 
class EscalationDecider: 
    def decide(self, issue, classification, context): 
        risk = classification['risk_level'] 
        if risk == 'critical': 
            return {'should_escalate': True, 'status': 'escalated', 'reason': 'Critical issue requires human handling'} 
        if risk == 'high': 
            return {'should_escalate': True, 'status': 'escalated', 'reason': 'High risk - needs human review'} 
        return {'should_escalate': False, 'status': 'replied', 'reason': 'Can be answered from documentation'} 
