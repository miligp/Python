import praw
import urllib.request
import xmltodict
import pandas as pd
from Document import DocumentFactory
from Corpus import Corpus

# Initialisation des configurations
REDDIT_CLIENT_ID = '2IwlmGw7CnMx_lNz12WACw'
REDDIT_CLIENT_SECRET = 'qIGIrg1hv4PJ6FhMSeWdLJ0Tt_sOaw'
REDDIT_USER_AGENT = 'TD3'

def fetch_reddit_posts(keyword, limit=100):
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         user_agent=REDDIT_USER_AGENT)
    subreddit = reddit.subreddit("all")
    posts = []
    for post in subreddit.search(keyword, limit=limit):
        posts.append({
            "title": post.title,
            "author": post.author.name if post.author else "Anonymous",
            "date": post.created_utc,
            "url": post.url,
            "text": post.selftext.replace('\n', ' '),
            "comments": post.num_comments
        })
    return posts

def fetch_arxiv_papers(keyword, max_results=100):
    url = f"http://export.arxiv.org/api/query?search_query=all:{keyword}&start=0&max_results={max_results}"
    response = urllib.request.urlopen(url).read()
    data = xmltodict.parse(response)
    papers = []
    for entry in data['feed']['entry']:
        authors = [author['name'] for author in entry['author']] if isinstance(entry['author'], list) else [entry['author']['name']]
        papers.append({
            "title": entry['title'],
            "author": authors[0],
            "date": entry['published'],
            "url": entry['id'],
            "text": entry['summary'],
            "co_authors": authors[1:]
        })
    return papers

if __name__ == "__main__":
    corpus = Corpus("Food Corpus")

    # Récupérer les données Reddit
    reddit_data = fetch_reddit_posts("Food", limit=100)
    for post in reddit_data:
        doc = DocumentFactory.create_document("reddit", post['title'], post['author'], post['date'], post['url'], post['text'], post['comments'])
        corpus.add_document(doc)

    # Récupérer les données Arxiv
    arxiv_data = fetch_arxiv_papers("Food", max_results=100)
    for paper in arxiv_data:
        doc = DocumentFactory.create_document("arxiv", paper['title'], paper['author'], paper['date'], paper['url'], paper['text'], paper['co_authors'])
        corpus.add_document(doc)

    # Sauvegarde du corpus
    corpus.save("Food_corpus.pkl")

    # Charger et afficher les données
    loaded_corpus = Corpus.load("Food_corpus.pkl")
    print(loaded_corpus)
    print(loaded_corpus.id2doc['D1'].getType())  # Affiche le type du premier document
