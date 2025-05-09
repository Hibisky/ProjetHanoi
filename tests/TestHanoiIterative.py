import unittest
from BlocAlgo.HanoiIterative import HanoiIterative  # Adapter le nom du fichier si nécessaire

class TestHanoiIterative(unittest.TestCase):

    def test_nombre_mouvements(self):
        for n in range(1, 6):  # On teste de 1 à 5 palets
            hanoi = HanoiIterative(n)
            expected_moves = 2 ** n - 1
            self.assertEqual(len(hanoi.movements), expected_moves, f"Nombre de mouvements incorrect pour {n} palets")

    def test_validite_mouvements(self):
        hanoi = HanoiIterative(3)
        towers = {1: [], 2: [], 3: []}
        towers[1] = list(reversed(range(1, 4)))

        for move in hanoi.movements:
            _, from_tower, to_tower, _, _ = move
            if not towers[from_tower]:
                raise ValueError(f"Tentative de déplacer depuis une tour vide : tour {from_tower}")
            palet = towers[from_tower].pop()
            if towers[to_tower] and towers[to_tower][-1] < palet:
                self.fail(f"Palet plus grand placé sur un plus petit : {palet} sur {towers[to_tower][-1]}")
            towers[to_tower].append(palet)

    def test_position_finale(self):
        for n in range(1, 5):
            hanoi = HanoiIterative(n)
            expected = list(reversed(range(1, n+1)))
            self.assertEqual(hanoi.towers[1], [], "La tour source doit être vide")
            self.assertEqual(hanoi.towers[2], [], "La tour auxiliaire doit être vide")
            self.assertEqual(hanoi.towers[3], expected, f"Les palets doivent être tous sur la tour destination pour {n} palets")

    def test_get_move_matrix_dict_format(self):
        hanoi = HanoiIterative(2)
        move_matrix = hanoi.get_move_matrix(as_dict=True)
        self.assertTrue(isinstance(move_matrix[0], dict))
        expected_keys = {"coup", "origine", "destination", "palets_origine_avant", "palets_destination_avant"}
        self.assertEqual(set(move_matrix[0].keys()), expected_keys)

if __name__ == "__main__":
    unittest.main()
