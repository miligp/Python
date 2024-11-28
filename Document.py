class Document:
    def __init__(self, title, author, date, url, text):
        self.title = title
        self.author = author  # Assurez-vous que c'est "author" ici
        self.date = date
        self.url = url
        self.text = text

    def __str__(self):
        return f"Document: {self.title} by {self.author} ({self.date})"

    def getType(self):
        return "Generic"
    

#=========================TD5 ============================================
class RedditDocument(Document):
    def __init__(self, title, author, date, url, text, num_comments):
        super().__init__(title, author, date, url, text)
        self.num_comments = num_comments

    def __str__(self):
        return f"Reddit Post: {self.title} ({self.num_comments} commentaires)"

    def getType(self):
        return "Reddit"
    

class ArxivDocument(Document):
    def __init__(self, title, author, date, url, text, co_authors):
        super().__init__(title, author, date, url, text)
        self.co_authors = co_authors

    def __str__(self):
        return f"Arxiv Paper: {self.title} avec co-authors {', '.join(self.co_authors)}"

    def getType(self):
        return "Arxiv"


class DocumentFactory:
    @staticmethod
    def create_document(doc_type, title, author, date, url, text, additional_info):
        if doc_type == "reddit":
            return RedditDocument(title, author, date, url, text, additional_info)
        elif doc_type == "arxiv":
            return ArxivDocument(title, author, date, url, text, additional_info)
        else:
            raise ValueError(f"Document inconnu type: {doc_type}")
