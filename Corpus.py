import re
import pandas as pd
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
        """
        Ajoute un document au corpus et met à jour les auteurs.
        """
        doc_id = f"D{self.ndoc + 1}"
        self.id2doc[doc_id] = document
        self.ndoc += 1

        # Gestion des auteurs
        if document.author not in self.authors:
            self.authors[document.author] = Author(document.author)
            self.naut += 1
        self.authors[document.author].add_document(document)

    def save(self, filename):
        """
        Sauvegarde le corpus dans un fichier pickle.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print(f"Corpus sauvegardé sous : {filename}")

    @staticmethod
    def load(filename):
        """
        Charge un corpus depuis un fichier pickle.
        """
        with open(filename, 'rb') as f:
            return pickle.load(f)

    def __repr__(self):
        """
        Affiche un résumé du corpus.
        """
        return f"Corpus: {self.name}, Documents: {self.ndoc}, Auteurs : {self.naut}"

    def get_all_texts(self):
        """
        Concatène et retourne tous les textes des documents du corpus.
        """
        return " ".join(doc.text for doc in self.id2doc.values())

    def search(self, mot_cle):
        """
        Recherche les occurrences d'un mot-clé dans le corpus.
        """
        all_texts = self.get_all_texts()
        pattern = re.compile(rf"\b{mot_cle}\b", re.IGNORECASE)
        matches = pattern.finditer(all_texts)
        start_positions = [m.start() for m in matches]
        print(f"{len(start_positions)} occurrences trouvées.")
        return [all_texts[max(0, i - 20):i + 20] for i in start_positions]

    def concorde(self, mot_cle, taille):
        """
        Construit un concordancier pour une expression donnée.
        """
        all_texts = self.get_all_texts()
        pattern = re.compile(rf"\b{mot_cle}\b", re.IGNORECASE)
        matches = pattern.finditer(all_texts)
        pos_pattern = [m.span() for m in matches]

        if not pos_pattern:
            print(f"Aucune occurrence trouvée pour le mot-clé '{mot_cle}'.")
            return pd.DataFrame(columns=["Contexte gauche", "Motif trouvé", "Contexte droit"])

        # Crée les contextes pour le concordancier
        context_left = pd.DataFrame(["..." + all_texts[max(0, i - taille):i] for (i, j) in pos_pattern])
        center = pd.DataFrame([all_texts[i:j] for (i, j) in pos_pattern])
        context_right = pd.DataFrame([all_texts[j:min(len(all_texts), j + taille)] + "..." for (i, j) in pos_pattern])

        # Combine les données pour le concordancier
        result = pd.concat([context_left, center, context_right], axis=1)
        result.columns = ["Contexte gauche", "Motif trouvé", "Contexte droit"]
        return result

    def stats(self, nreturn=10):
        """
        Affiche les statistiques textuelles du corpus.
        """
        words = [word for doc in self.id2doc.values() for word in doc.text.split()]
        word_freq = pd.Series(words).value_counts()
        print(f"{len(words)} mots dans le corpus.")
        print("Mots les plus fréquents :")
        print(word_freq.head(nreturn).to_string())
        return word_freq.to_dict()

