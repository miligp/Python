# Projet Moteur de Recherche (Python)

Projet Python Ilyna Machane &amp; Milena Gordien Piquet

Ce projet est un moteur de recherche conçu pour analyser un corpus textuel que nous avons créé en utilisant des posts de Reddit et des articles d'Arxiv.

## Fonctionnalités

### Récupération de données :
- Récupération des posts de Reddit (api PRAW).
- Récupération des articles d'Arxiv (api libre urllib)
 
### Création du Corpus :
- Stocke les données récupérées dans un objet Corpus, chaque document étant associé à un auteur et enregistré en fonction des specifications du document.
- Le corpus est sauvegardé et chargé via la bibliothèque pickle.

### Moteur de Recherche :
- Génère des matrices de Fréquence de Termes (TF) et TF-IDF pour noter les documents selon leur pertinence.
- Permet des recherches par mot-clé donné par l'utilisateur.

## Utilisation du moteur de recherche 

Après avoir cloné le programme et vérifié si le corpus Food_corpus.pkl est présent, il faut lancer le notebook (Jupyter) Interface.ipynb et lancer le « run all». 

Pour effectuer une recherche, il faut se trouver dans l'interface : Moteur de recherche contenue dans le Note Book. 

Vous trouverez une case Mot-cl. Il suffira d'entrer le mot, de choisir un nombre de documents que vous voulez voir apparaitre et de cliquer sur rechercher pour trouver des documents du corpus en rapport avec votre mot. 

