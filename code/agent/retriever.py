# Retriever module 
 
class SupportRetriever: 
    def __init__(self, corpus_path='../data'): 
        self.corpus_path = corpus_path 
 
    def retrieve(self, query, domain=None, k=5): 
        return [] 
 
    def get_context_string(self, docs): 
        return "Based on available documentation" 
