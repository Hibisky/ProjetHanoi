import logging
from Filtrer_analyseAlgo import AnalyseAlgo

class HanoiIterative:
    def __init__(self, nb_palet_camera):
        """
        Initialise la classe avec le nombre de palets à déplacer.
        :param nb_palet_camera: Nombre de palets à utiliser dans la tour de Hanoï.
        """
        self.nb_palet_camera = nb_palet_camera  # Stocke le nombre de palets
        self.movements = []  # Liste qui contiendra les mouvements effectués
        # Initialise les trois tours avec les palets empilés sur la première tour
        self.towers = {1: list(reversed(range(1, nb_palet_camera + 1))), 2: [], 3: []}
        self.solve()                      # Genere les mouvements pour faire un minimum de deplacement
        #self.afficher_mouvements()        # Affiche les mouvements effectués sous forme de tableau 

    def solve(self):
        """
        Résout le problème de la Tour de Hanoï de manière itérative.
        Enregistre chaque mouvement dans la liste `movements`.
        """
        source, auxiliary, destination = 1, 2, 3

        if self.nb_palet_camera % 2 == 0:
            auxiliary, destination = destination, auxiliary

        total_moves = (2 ** self.nb_palet_camera) - 1

        for move in range(1, total_moves + 1):
            # Choix initial des tours
            # Détermine quel mouvement effectuer en fonction du numéro du coup
            if move % 3 == 1:
                from_tower, to_tower = source, destination
            elif move % 3 == 2:
                from_tower, to_tower = source, auxiliary
            else:
                from_tower, to_tower = auxiliary, destination

            # Vérifie et effectue le mouvement du palet selon les règles du jeu
            if self.towers[from_tower] and (not self.towers[to_tower] or self.towers[from_tower][-1] < self.towers[to_tower][-1]):
                nb_palets_origine_avant = len(self.towers[from_tower])
                nb_palets_destination_avant = len(self.towers[to_tower])
                palet = self.towers[from_tower].pop()
                self.towers[to_tower].append(palet)
            elif self.towers[to_tower] and (not self.towers[from_tower] or self.towers[to_tower][-1] < self.towers[from_tower][-1]):
                nb_palets_origine_avant = len(self.towers[to_tower])
                nb_palets_destination_avant = len(self.towers[from_tower])
                palet = self.towers[to_tower].pop()
                self.towers[from_tower].append(palet)
                from_tower, to_tower = to_tower, from_tower  # Corrige l'ordre des tours

            # Enregistre le mouvement
            self.movements.append((
                move, from_tower, to_tower, nb_palets_origine_avant, nb_palets_destination_avant
            ))

    def get_move_matrix(self, as_dict=False):
        """
        Retourne la liste des mouvements sous forme de matrice.
        :param as_dict: True pour avoir une liste de dictionnaires.
        """
        if as_dict:
            return [
                {
                    "coup": m[0],
                    "origine": m[1],
                    "destination": m[2],
                    "palets_origine_avant": m[3],
                    "palets_destination_avant": m[4]
                } for m in self.movements
            ]
        return self.movements

    def afficher_mouvements(self):
        """
        Affiche les mouvements du jeu de Hanoï sous forme de tableau.
        """
        print("\n=== Mouvements du jeu de Hanoï ===")
        print(f"{'Coup':<6}{'Origine':<8}{'Destination':<12}{'Palets Org Av':<15}{'Palets Dest Av'}")
        print("-" * 65)

        for move in self.movements:
            print(f"{move[0]:<6}{move[1]:<8}{move[2]:<12}{move[3]:<22}{move[4]}")


if __name__ == "__main__":
    n_palets = 4 # Test avec 4 palets
    analyse = AnalyseAlgo() # permet une verification de l'algo generé par hanoi
    hanoi = HanoiIterative(n_palets)
    move = hanoi.get_move_matrix()
    hanoi.afficher_mouvements()
    analyse.verifier_mouvements(move,n_palets)