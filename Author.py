class Author:
    def __init__(self, name):
        self.name = name
        self.documents = []

    def add_document(self, document):
        self.documents.append(document)

    def get_statistics(self):
        total_documents = len(self.documents)
        avg_length = sum(len(doc.text) for doc in self.documents) / total_documents
        return total_documents, avg_length

    def __str__(self):
        return f"Auteur: {self.name}, Documents: {len(self.documents)}"