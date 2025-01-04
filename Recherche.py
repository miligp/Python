import re
import numpy as np
import scipy.sparse as sp
from Corpus import Corpus  
from tabulate import tabulate

def construire_vocabulaire(corpus):
    vocab = {}
    voc_stats = corpus.stats()
    for idx, word in enumerate(sorted(voc_stats.keys()), start=1):
        vocab[word] = {'id': idx, 'occ': voc_stats[word]}
    return vocab


def construire_matrice_TF(corpus, vocab):
    rows, cols, data = [], [], []
    for i, doc in enumerate(corpus.id2doc.values()):
        words = doc.text.lower().split()
        for word in words:
            if word in vocab:
                rows.append(i)
                cols.append(vocab[word]['id'] - 1)
                data.append(1)

    n_docs = len(corpus.id2doc)
    n_words = len(vocab)
    mat_TF = sp.csr_matrix((data, (rows, cols)), shape=(n_docs, n_words))
    return mat_TF


def construire_matrice_TFIDF(mat_TF, vocab):
    n_docs = mat_TF.shape[0]
    doc_freq = np.array(mat_TF.sum(axis=0)).flatten()
    idf = np.log(n_docs / (1 + doc_freq))
    mat_TFIDF = mat_TF.multiply(idf)
    return mat_TFIDF


def recherche(mat_TFIDF, vocab, query_words):
    if isinstance(query_words, str):
        query_words = query_words.lower().split()

    query_vec = np.zeros(len(vocab))
    for word in query_words:
        if word in vocab:
            query_vec[vocab[word]['id'] - 1] = 1

    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        print("La requête est vide ou ne contient aucun mot du vocabulaire.")
        return None, None

    doc_norms = np.sqrt(mat_TFIDF.multiply(mat_TFIDF).sum(axis=1)).A.flatten()
    cos_sim = np.zeros(mat_TFIDF.shape[0])
    for i, doc_norm in enumerate(doc_norms):
        if doc_norm != 0:
            cos_sim[i] = mat_TFIDF.getrow(i).dot(query_vec).item() / (doc_norm * query_norm)

    most_similar_docs = np.argsort(cos_sim)[::-1]  
    return cos_sim, most_similar_docs

def afficher_resultats(resultats, max_content_len=100):
    # Limiter la longueur du contenu pour chaque document
    for resultat in resultats:
        resultat['Contenu'] = (resultat['Contenu'][:max_content_len] + '...') if len(resultat['Contenu']) > max_content_len else resultat['Contenu']
    
    # Afficher les résultats dans un tableau propre
    print(tabulate(resultats, headers="keys", tablefmt="pretty", maxcolwidths=[None, None, max_content_len]))

if __name__ == "__main__":
    try:
        corpus = Corpus.load("Food_corpus.pkl")
    except FileNotFoundError:
        print("Le fichier 'Food_corpus.pkl' est introuvable. Veuillez le générer.")
        exit(1)

    print("Construction du vocabulaire...")
    vocabulaire = construire_vocabulaire(corpus)
    print(f"Vocabulaire construit : {len(vocabulaire)} mots.")

    print("\nConstruction de la matrice TF...")
    mat_TF = construire_matrice_TF(corpus, vocabulaire)
    print(f"Matrice TF construite : {mat_TF.shape}.")

    print("\nConstruction de la matrice TF-IDF...")
    mat_TFIDF = construire_matrice_TFIDF(mat_TF, vocabulaire)
    print(f"Matrice TF-IDF construite : {mat_TFIDF.shape}.")

    query_word = "digital"
    print(f"\n=== Recherche pour le mot : '{query_word}' ===")
    scores, most_similar_docs = recherche(mat_TFIDF, vocabulaire, query_word)

    if scores is not None:
        resultats = []
    
        # Parcourir les indices des documents pertinents
        for doc_idx in most_similar_docs[:3]:  # Récupérer les 5 documents les plus pertinents
            doc_id = doc_idx + 1
            doc_text = corpus.id2doc[f'D{doc_id}'].text[:250]  # Extraire les 200 premiers caractères du document
            resultats.append({
                "Document ID": doc_id,
                "Score de similarité": round(scores[doc_idx], 4),
                "Contenu": doc_text
            })
        
        # Appeler la fonction pour afficher les résultats dans un tableau bien formaté
        afficher_resultats(resultats, max_content_len=100)
    else:
        print("Aucun résultat pertinent.")