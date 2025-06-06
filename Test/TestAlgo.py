import unittest
from BlocAlgo.HanoiIterative import HanoiIterative  

class TestAlgo(unittest.TestCase):

    def test_nombre_mouvements(self):
        """
        Vérifie que le nombre de mouvements générés par l'algorithme
        correspond bien à la formule mathématique : 2^n - 1.
        """
        for n in range(1, 6):  # Test de 1 à 5 palets
            hanoi = HanoiIterative(n)
            expected_moves = 2 ** n - 1
            self.assertEqual(len(hanoi.movements), expected_moves,
                             f"Nombre de mouvements incorrect pour {n} palets")

    def test_validite_mouvements(self):
        """
        Vérifie que chaque mouvement respecte les règles du jeu :
        - Un palet ne peut être posé que sur un palet plus grand ou une tour vide.
        """
        hanoi = HanoiIterative(3)
        towers = {1: list(reversed(range(1, 4))), 2: [], 3: []}  # Réinitialisation des tours

        for move in hanoi.movements:
            _, from_tower, to_tower, _, _ = move

            # Simulation du déplacement pour vérifier la validité
            if not towers[from_tower]:
                raise ValueError(f"Tentative de déplacer depuis une tour vide : tour {from_tower}")

            palet = towers[from_tower].pop()

            if towers[to_tower] and towers[to_tower][-1] < palet:
                self.fail(f"Palet plus grand placé sur un plus petit : {palet} sur {towers[to_tower][-1]}")

            towers[to_tower].append(palet)

    def test_position_finale(self):
        """
        Vérifie qu’à la fin de l’algorithme, tous les palets sont bien empilés
        dans l'ordre correct sur la troisième tour.
        """
        for n in range(1, 5):  # Teste avec 1 à 4 palets
            hanoi = HanoiIterative(n)
            expected = list(reversed(range(1, n + 1)))

            # Vérifie que les deux premières tours sont vides
            self.assertEqual(hanoi.towers[1], [], "La tour source doit être vide")
            self.assertEqual(hanoi.towers[2], [], "La tour auxiliaire doit être vide")

            # Vérifie que la tour destination contient tous les palets dans le bon ordre
            self.assertEqual(hanoi.towers[3], expected,
                             f"Les palets doivent être tous sur la tour destination pour {n} palets")

    def test_get_move_matrix_dict_format(self):
        """
        Vérifie que la méthode `get_move_matrix(as_dict=True)` retourne une liste de dictionnaires
        avec les bonnes clés.
        """
        hanoi = HanoiIterative(2)
        move_matrix = hanoi.get_move_matrix(as_dict=True)

        self.assertTrue(isinstance(move_matrix[0], dict), "Chaque élément doit être un dictionnaire")
        
        expected_keys = {"coup", "origine", "destination", "palets_origine_avant", "palets_destination_avant"}
        self.assertEqual(set(move_matrix[0].keys()), expected_keys,
                         "Les clés des dictionnaires sont incorrectes")

if __name__ == "__main__":
    unittest.main()
