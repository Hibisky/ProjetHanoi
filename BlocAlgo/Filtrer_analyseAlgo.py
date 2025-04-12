import logging

class AnalyseAlgo:
    def __init__(self):
        # Configuration du logger pour enregistrer les logs dans un fichier
        logging.basicConfig(
            level=logging.DEBUG,  # Niveau de log pour tout afficher
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                #logging.StreamHandler(),  # Affichage dans le terminal
                logging.FileHandler('analyse_algo.log', mode='w')  # Enregistrement dans le fichier log
            ]
        )

    def verifier_mouvements(self, movements, nb_palet):
        """
        Vérifie la validité des mouvements générés pour le problème de Hanoï et enregistre les erreurs dans le fichier de log.

        Args:
            movements: liste de tuples (move, origine, destination, nb_orig_av, nb_dest_av)
            nb_palet: nombre de palets total au départ
        """
        # Initialiser les tours
        tours = {
            1: list(range(nb_palet, 0, -1)),  # Palets de plus grand à plus petit
            2: [],
            3: []
        }

        logging.info("\n📋 Vérification des mouvements...\n")

        for mvt in movements:
            coup, origine, destination, nb_orig_av, nb_dest_av = mvt

            # Vérification du nombre de palets avant déplacement
            if len(tours[origine]) != nb_orig_av or len(tours[destination]) != nb_dest_av:
                error_message = f"❌ Erreur au coup {coup}:"
                error_message += f"\n   Origine: Tour {origine} contient {len(tours[origine])} palets (attendu: {nb_orig_av})"
                error_message += f"\n   Destination: Tour {destination} contient {len(tours[destination])} palets (attendu: {nb_dest_av})"
                error_message += f"\n   État actuel: T1={tours[1]}, T2={tours[2]}, T3={tours[3]}\n"
                logging.error(error_message)  # Enregistrement de l'erreur dans le log

            # Exécuter le déplacement
            if not tours[origine]:
                logging.warning(f"⚠️ Coup {coup}: tentative de déplacer depuis une tour vide ({origine})\n")
                continue

            palet = tours[origine].pop()
            if tours[destination] and palet > tours[destination][-1]:
                logging.error(f"🚫 Coup {coup}: palet {palet} ne peut pas être placé sur {tours[destination][-1]} (Tour {destination})\n")
            tours[destination].append(palet)

        logging.info("✅ Vérification terminée.\n")


# Exemple d'utilisation
if __name__ == "__main__":
    analyse = AnalyseAlgo()

    n_palet = 5
    mouvements = [
        (1, 1, 3, 5, 0),
        (2, 1, 2, 4, 0),
        (3, 2, 3, 2, 1),  # Exemple où une erreur pourrait se produire
        (4, 1, 2, 3, 0),
        (5, 1, 3, 2, 0),
    ]
    # Appel de la méthode de vérification des mouvements
    analyse.verifier_mouvements(mouvements, n_palet)



#### Logique du test de la matrice 


### MATRICE POUR 4 PALETS

# Coup	Description de l’erreur
# 3 : déplacement depuis une tour vide.
# 5 : taille de palet incorrecte (palet plus grand placé sur un plus petit).
# 6 : nombre de palets origine erroné (simule une erreur dans le log).
# 7 : nombre de palets destination erroné.

#     mauvais_mouvements = [
#     (1, 1, 3, 4, 0),  # OK
#     (2, 1, 2, 3, 0),  # OK
#     (3, 2, 3, 0, 1),  # ❌ Déplacement depuis une tour vide: Tour 2 vide
#     (4, 1, 3, 2, 2),  # OK
#     (5, 2, 3, 1, 3),  # 🚫 taille de palet incorrecte: Palet plus grand placé sur plus petit
#     (6, 1, 2, 5, 1),  # ❌ Mauvais nb palets origine (il y en aura moins que 5)
#     (7, 3, 1, 4, 3),  # ❌ Mauvais nb palets destination
#     (8, 3, 2, 3, 1),  # OK
# ]
        
### MATRICE POUR 5 PALETS
    
# Coup	Description de l’erreur
# 5	  :  🚫 Palet plus grand sur palet plus petit : palet 1 essaie d’être placé sur 5
# 6	  :  ⚠️ Tour vide après coup 5, la tour 2 est censée être vide à cause de l’erreur précédente
# 7	  :  ❌ Mouvement impossible : palet 5 sur 2, il est plus grand que le palet actuellement sur 2
# 8	  :  ❌ Mauvais nombre de palets destination (1 palet au lieu de 2)
# 10  :  🚫 Palet plus grand sur plus petit : palet 4 sur palet 1 (Tour 3)
# 21  :	 🚫 Palet plus grand sur palet plus petit : palet 2 sur palet 3
# 23  :	 ❌ Mauvais mouvement de la tour 1, la source est incorrecte
# 25  :	 🚫 Mauvais mouvement de la tour 2 après l’erreur précédente
# 28  :	 🚫 Palet plus grand sur plus petit : palet 5 sur palet 1 sur Tour 3
        
#     mauvais_mouvements = [
#     (1, 1, 3, 5, 0),   # ✅ OK (5 va sur 3)
#     (2, 1, 2, 4, 0),   # ✅ OK (4 va sur 2)
#     (3, 3, 2, 1, 1),   # ✅ OK (1 va sur 2)
#     (4, 1, 3, 3, 0),   # ✅ OK (3 va sur 3)
#     (5, 2, 1, 2, 2),   # 🚫 Erreur : palet 1 ne peut pas aller sur 5
#     (6, 2, 3, 1, 1),   # ⚠️ Tour 2 vide après coup 5
#     (7, 1, 2, 3, 0),   # ❌ Erreur : mouvement impossible de la tour 1 vers la 2 (palet plus grand)
#     (8, 1, 2, 2, 2),   # ❌ Erreur : mauvais nb palets destination (1 palet sur 2)
#     (9, 3, 1, 2, 1),   # ✅ OK (1 retourne sur 1)
#     (10, 2, 3, 2, 1),  # 🚫 Erreur : palet 4 sur plus petit (palet 1 ou 3)
#     (11, 1, 2, 3, 1),  # ✅ OK (3 va sur 2)
#     (12, 1, 3, 2, 1),  # ✅ OK (3 va sur 3)
#     (13, 2, 3, 2, 1),  # ✅ OK (2 va sur 3)
#     (14, 1, 2, 2, 2),  # ✅ OK (5 va sur 2)
#     (15, 3, 1, 2, 2),  # ✅ OK (2 va sur 1)
#     (16, 2, 1, 1, 3),  # ✅ OK (3 retourne sur 1)
#     (17, 3, 1, 1, 3),  # ✅ OK (1 retourne sur 1)
#     (18, 2, 3, 1, 1),  # ✅ OK (1 va sur 3)
#     (19, 1, 3, 2, 1),  # ✅ OK (2 retourne sur 3)
#     (20, 1, 2, 3, 1),  # ✅ OK (5 va sur 2)
#     (21, 1, 3, 2, 2),  # 🚫 Erreur : palet plus grand que le suivant (2 va sur 3)
#     (22, 2, 3, 1, 2),  # ✅ OK (1 retourne sur 3)
#     (23, 1, 2, 1, 3),  # ❌ Mauvais mouvement de la tour 1
#     (24, 3, 1, 1, 2),  # ✅ OK (2 va sur 1)
#     (25, 2, 1, 3, 3),  # 🚫 Mauvais mouvement de la tour 2
#     (26, 1, 3, 2, 2),  # ✅ OK (2 va sur 3)
#     (27, 1, 3, 1, 2),  # ✅ OK (1 va sur 3)
#     (28, 2, 3, 1, 3),  # 🚫 Mauvais palet sur palet plus petit
#     (29, 1, 3, 2, 1),  # ✅ OK (3 retourne sur 3)
#     (30, 3, 2, 2, 2),  # ✅ OK (1 retourne sur 2)
#     (31, 2, 1, 3, 2)   # ✅ OK (palet plus petit retourne sur 1)
# ]

#### RESULTATS ANALYSE POUR 4 PALETS
#     Vérification des mouvements...

# ❌ Erreur au coup 3:
#    Origine: Tour 2 contient 1 palets (attendu: 0)
#    Destination: Tour 3 contient 1 palets (attendu: 1)
#    État actuel: T1=[4, 3], T2=[2], T3=[1]

# 🚫 Coup 3: palet 2 ne peut pas être placé sur 1 (Tour 3)

# 🚫 Coup 4: palet 3 ne peut pas être placé sur 2 (Tour 3)

# ❌ Erreur au coup 5:
#    Origine: Tour 2 contient 0 palets (attendu: 1)
#    Destination: Tour 3 contient 3 palets (attendu: 3)
#    État actuel: T1=[4], T2=[], T3=[1, 2, 3]

# ⚠️ Coup 5: tentative de déplacer depuis une tour vide (2)

# ❌ Erreur au coup 6:
#    Origine: Tour 1 contient 1 palets (attendu: 5)
#    Destination: Tour 2 contient 0 palets (attendu: 1)
#    État actuel: T1=[4], T2=[], T3=[1, 2, 3]

# ❌ Erreur au coup 7:
#    Origine: Tour 3 contient 3 palets (attendu: 4)
#    Destination: Tour 1 contient 0 palets (attendu: 3)
#    État actuel: T1=[], T2=[4], T3=[1, 2, 3]

# ❌ Erreur au coup 8:
#    Origine: Tour 3 contient 2 palets (attendu: 3)
#    Destination: Tour 2 contient 1 palets (attendu: 1)
#    État actuel: T1=[3], T2=[4], T3=[1, 2]

# ✅ Vérification terminée.