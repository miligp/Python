import re
import numpy as np
import scipy.sparse as sp
from Corpus import Corpus
import pandas as pd
from tqdm import tqdm

class SearchEngine:
    def __init__(self, corpus):
        self.corpus = corpus
        self.vocabulaire = self._construire_vocabulaire(afficher_stats=False)
        
        print("\nConstruction du vocabulaire...")
        print(f"Vocabulaire construit : {len(self.vocabulaire)} mots.")
        
        print("\nConstruction de la matrice TF...")
        self.mat_TF = self._construire_matrice_TF()
        print(f"Matrice TF construite : {self.mat_TF.shape}.")
        
        print("\nConstruction de la matrice TF-IDF...")
        self.mat_TFIDF = self._construire_matrice_TFIDF()
        print(f"Matrice TF-IDF construite : {self.mat_TFIDF.shape}.")

    def _construire_vocabulaire(self, afficher_stats=False):
        vocab = {}
        voc_stats = self.corpus.stats()
        
        # N'affiche les stats que si demandé
        if afficher_stats:
            print(f"{len(voc_stats)} mots dans le corpus.")
            print("Mots les plus fréquents :")
            for word, count in sorted(voc_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"{word:8} {count}")
        
        for idx, word in enumerate(sorted(voc_stats.keys()), start=1):
            vocab[word] = {
                'id': idx,
                'occ': voc_stats[word],
                'doc_count': 0
            }
        
        for doc in self.corpus.id2doc.values():
            words = set(doc.text.lower().split())
            for word in words:
                if word in vocab:
                    vocab[word]['doc_count'] += 1

        return vocab

    def _construire_matrice_TF(self):
        rows, cols, data = [], [], []
        for i, doc in enumerate(self.corpus.id2doc.values()):
            words = doc.text.lower().split()
            for word in words:
                if word in self.vocabulaire:
                    rows.append(i)
                    cols.append(self.vocabulaire[word]['id'] - 1)
                    data.append(1)

        n_docs = len(self.corpus.id2doc)
        n_words = len(self.vocabulaire)
        mat_TF = sp.csr_matrix((data, (rows, cols)), shape=(n_docs, n_words))
        return mat_TF

    def _construire_matrice_TFIDF(self):
        n_docs = self.mat_TF.shape[0]
        doc_freq = np.array(self.mat_TF.sum(axis=0)).flatten()
        idf = np.log(n_docs / (1 + doc_freq))
        mat_TFIDF = self.mat_TF.multiply(idf)
        return mat_TFIDF

    def _recherche(self, query_words):
        if isinstance(query_words, str):
            query_words = query_words.lower().split()

        query_vec = np.zeros(len(self.vocabulaire))
        for word in query_words:
            if word in self.vocabulaire:
                query_vec[self.vocabulaire[word]['id'] - 1] = 1

        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            print("La requête est vide ou ne contient aucun mot du vocabulaire.")
            return None, None

        doc_norms = np.sqrt(self.mat_TFIDF.multiply(self.mat_TFIDF).sum(axis=1)).A.flatten()
        cos_sim = np.zeros(self.mat_TFIDF.shape[0])
        for i, doc_norm in enumerate(doc_norms):
            if doc_norm != 0:
                cos_sim[i] = self.mat_TFIDF.getrow(i).dot(query_vec).item() / (doc_norm * query_norm)

        most_similar_docs = np.argsort(cos_sim)[::-1]
        return cos_sim, most_similar_docs

    def search(self, query_words, n_results=5):
        print(f"\n=== Recherche pour le mot : '{query_words}' ===")
        scores, most_similar_docs = self._recherche(query_words)
        
        if scores is not None:
            resultats = []
            for doc_idx in tqdm(most_similar_docs[:n_results],
                              desc="Formatage des résultats",
                              total=min(n_results, len(most_similar_docs))):
                doc_id = doc_idx + 1
                doc_text = self.corpus.id2doc[f'D{doc_id}'].text[:250]
                resultats.append({
                    "Document ID": doc_id,
                    "Score de similarité": round(scores[doc_idx], 4),
                    "Contenu": doc_text
                })
            df_resultats = pd.DataFrame(resultats)
            return df_resultats
        else:
            print("Aucun résultat pertinent.")
            return pd.DataFrame()

# # Code principal
# if __name__ == "__main__":
#     try:
#         # Chargement du corpus
#         corpus = Corpus.load("Food_corpus.pkl")
        
#         # Affichage initial des statistiques
#         stats = corpus.stats()
#         print(f"{len(stats)} mots dans le corpus.")
#         print("Mots les plus fréquents :")
#         for word, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]:
#             print(f"{word:8} {count}")
        
#         # Création du moteur de recherche sans réafficher les stats
#         moteur = SearchEngine(corpus)
        
#         # Interface de recherche
#         query_word = input("\nEntrez vos mots-clés pour la recherche : ")
#         resultats = moteur.search(query_word, n_results=3)

#         if not resultats.empty:
#             print("\n=== Résultats de la recherche ===")
#             print(resultats)
#         else:
#             print("Aucun résultat trouvé.")
            
#     except FileNotFoundError:
#         print("Le fichier 'Food_corpus.pkl' est introuvable. Veuillez le générer.")
#         exit(1)