import pickle
from Author import Author

class Corpus:
    def __init__(self, name):
        self.name = name
        self.id2doc = {}
        self.authors = {}
        self.ndoc = 0
        self.naut = 0

    def add_document(self, document):
        doc_id = f"D{self.ndoc + 1}"
        self.id2doc[doc_id] = document
        self.ndoc += 1

        # Gestion des auteurs
        if document.author not in self.authors:
            self.authors[document.author] = Author(document.author)
            self.naut += 1
        self.authors[document.author].add_document(document)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print(f"Corpus saved to {filename}")

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def __repr__(self):
        return f"Corpus: {self.name}, Documents: {self.ndoc}, Authors: {self.naut}"
