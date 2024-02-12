Projet final IA101

NID.py est le fichier principal, il permet de prédire les prix suivant plusieurs stratégies en utilisant la distance NID
NCD.py est un fichier annexe, pas utilisé au final car la distance NCD n'était pas suffisamment bonne
neural_network.py est un réseau de neurones qui remplace la fonction f dans NID.py pour prédire le prix des NFT à partir des distances NID

sandbar, sandbar_dist et sandbar_price sont 3 fichiers qui stockent les données de la collection de NFT sandbar sur laquelle on s'est penché sur ce projet. Les scripts peuvent les recréer à chaque exécution mais les enregistrer permet d'accélerer l'exécution ainsi que permettre une reproductibilité des résultats car les prix et les listings peuvent être grandement modifiés d'une exécution à l'autre
