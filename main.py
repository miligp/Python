import os
from Corpus import Corpus
from Document import DocumentFactory
import praw
import urllib.request
import xmltodict
from Recherche import construire_vocabulaire, construire_matrice_TF, construire_matrice_TFIDF, recherche, afficher_resultats
from tabulate import tabulate

# Configuration pour récupérer les données Reddit
REDDIT_CLIENT_ID = '2IwlmGw7CnMx_lNz12WACw'
REDDIT_CLIENT_SECRET = 'qIGIrg1hv4PJ6FhMSeWdLJ0Tt_sOaw'
REDDIT_USER_AGENT = 'TD3'

# Fonction pour récupérer les posts Reddit
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

# Fonction pour récupérer les articles Arxiv
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


# Main script
if __name__ == "__main__":
    filename = "Food_corpus.pkl"
    keyword = "digital" 

    # Vérifier si un corpus existe déjà
    if os.path.exists(filename):
        print(f"Chargement du corpus existant : {filename}...")
        corpus = Corpus.load(filename)
    else:
        print(f"Fichier {filename} non trouvé. Création d'un nouveau corpus...")
        corpus = Corpus("Food Corpus")

        # Ajouter des documents Reddit
        reddit_data = fetch_reddit_posts("Food", limit=100)
        for post in reddit_data:
            doc = DocumentFactory.create_document("reddit", post['title'], post['author'], post['date'], post['url'], post['text'], post['comments'])
            corpus.add_document(doc)

        # Ajouter des documents Arxiv
        arxiv_data = fetch_arxiv_papers("Food", max_results=100)
        for paper in arxiv_data:
            doc = DocumentFactory.create_document("arxiv", paper['title'], paper['author'], paper['date'], paper['url'], paper['text'], paper['co_authors'])
            corpus.add_document(doc)

        # Sauvegarde du nouveau corpus
        corpus.save(filename)
        print(f"Nouveau corpus créé et sauvegardé sous {filename}.")

    # Étape 1 : Afficher un résumé du corpus
    print("\n=== Corpus chargé ===")
    print(corpus)

    # Étape 2 : Rechercher un mot-clé
    print("\n=== Recherche d'un mot-clé ===")
    results = corpus.search(keyword)

    if results:
        # Limiter à 10 résultats maximum
        limited_results = results[:10]
        for idx, result in enumerate(limited_results, 1):
            print(f"{idx}: {result}")
    else:
        print(f"Aucune occurrence trouvée pour le mot-clé '{keyword}'.")

    # Étape 3 : Créer un concordancier
    print("\n=== Concordancier ===")
    concorde = corpus.concorde(keyword, taille=30)
    print(concorde)


    # Intégration des fonctionnalités de recherche avancée
    # Construction du vocabulaire
    print("\nConstruction du vocabulaire...")
    vocabulaire = construire_vocabulaire(corpus)
    print(f"Vocabulaire construit : {len(vocabulaire)} mots.")

    # Construction de la matrice TF
    print("\nConstruction de la matrice TF...")
    mat_TF = construire_matrice_TF(corpus, vocabulaire)
    print(f"Matrice TF construite : {mat_TF.shape}.")

    # Construction de la matrice TF-IDF
    print("\nConstruction de la matrice TF-IDF...")
    mat_TFIDF = construire_matrice_TFIDF(mat_TF, vocabulaire)
    print(f"Matrice TF-IDF construite : {mat_TFIDF.shape}.")

    # Étape 5 : Rechercher un mot-clé avec le modèle TF-IDF
    print(f"\n=== Recherche pour le mot : '{keyword}' ===")
    scores, most_similar_docs = recherche(mat_TFIDF, vocabulaire, keyword)

    if scores is not None:
        resultats = []
        # Parcourir les indices des documents pertinents
        for doc_idx in most_similar_docs[:3]:  # Récupérer les 3 documents les plus pertinents
            doc_id = doc_idx + 1
            doc_text = corpus.id2doc[f'D{doc_id}'].text[:250]  # Extraire les 250 premiers caractères du document
            resultats.append({
                "Document ID": doc_id,
                "Score de similarité": round(scores[doc_idx], 4),
                "Contenu": doc_text
            })
        
        # Afficher les résultats
        afficher_resultats(resultats, max_content_len=100)
    else:
        print("Aucun résultat pertinent.")