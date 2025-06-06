import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer

from BlocAlgo.HanoiIterative import HanoiIterative

class SimulationMoves(QWidget):

    def __init__(self, algorithm, qapplication):
        """
        Initialise la fenêtre de simulation de la Tour de Hanoï.

        :param algorithm: HanoiIterative - Instance de l'algorithme contenant la solution.
        """
        super().__init__()
        self.qapplication = qapplication
        self.algorithm = algorithm
        self.tower_positions = [100, 300, 500]  # Positions des tours sur l'interface graphique
        self.palet_widths = [80, 70, 60, 50, 40][:self.algorithm.nb_palet_camera]  # Largeur des palets
        self.towers = {0: list(range(1, self.algorithm.nb_palet_camera + 1)), 1: [], 2: []}  # État initial des tours
        self.index = 0  # Indice du mouvement actuel
        self.movements = self.algorithm.get_move_matrix()  # Récupération des mouvements

        print("Movements received in simulation:", self.movements)

        self.setWindowTitle("Tower of Hanoi - PyQt6")
        self.setGeometry(100, 100, 600, 400)

        # Création du timer pour animer les mouvements
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_move)
        self.timer.start(1000)  # Déclenchement toutes les secondes

    def move_palet(self, source, destination):
        """
        Déplace un palet d'une tour à une autre.

        :param source: int - Index de la tour d'origine (0, 1 ou 2).
        :param destination: int - Index de la tour de destination (0, 1 ou 2).
        :return: Aucun (modifie self.towers).
        """
        if self.towers[source]:
            palet = self.towers[source].pop()
            self.towers[destination].append(palet)
        else:
            print(f"Erreur: Pas de palet à déplacer depuis la tour {source}")

    def next_move(self):
        """
        Exécute le prochain mouvement enregistré dans la solution.

        :return: Aucun (met à jour self.towers et rafraîchit l'affichage).
        """
        if self.index < len(self.movements):
            move_num, source, destination, palets_origin_before, palets_destination_before = self.movements[self.index]
            self.move_palet(source - 1, destination - 1)  # Ajustement pour indexation zéro
            print(f"Mouvement {move_num}: Tour {source} → Tour {destination} | Palets avant (Origine: {palets_origin_before}, Destination: {palets_destination_before})")
            self.index += 1
            self.update()  # Redessiner la fenêtre après chaque mouvement
        else:
            self.timer.stop()  # Arrêter le timer une fois tous les mouvements effectués

    def paintEvent(self, event):
        """
        Dessine les tours et les palets dans l'interface graphique.

        :param event: QPaintEvent - Événement de mise à jour de l'interface.
        :return: Aucun (affichage graphique des tours et palets).
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(255, 255, 255))  # Fond blanc

        # Dessiner les tours
        for x in self.tower_positions:
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawRect(x - 10, 100, 20, 200)  # Base des tours
            painter.drawEllipse(x - 15, 80, 30, 30)  # Dessus des tours

        # Dessiner les palets
        for i, tower in self.towers.items():
            for j, palet in enumerate(tower):
                palet_index = palet - 1
                if palet_index < len(self.palet_widths):  # Vérification pour éviter les erreurs d'indexation
                    painter.setBrush(QBrush(QColor(0, 0, 255)))  # palets en bleu
                    painter.drawRect(
                        self.tower_positions[i] - self.palet_widths[palet_index] // 2, 
                        280 - j * 20, 
                        self.palet_widths[palet_index], 20
                    )

        # Connecter le signal de fermeture de la fenêtre à la méthode __closeEvent
        self.closeEvent = self.__closeEvent

    def __closeEvent(self, event):
        """
        Gère la fermeture de la fenêtre de simulation.

        :param event: QCloseEvent - Événement de fermeture de la fenêtre.
        :return: Aucun (ferme l'application).
        """
        self.timer.stop()
        event.accept()
        print("Simulation fermée.")
        self.close()
        # Ferme l'application proprement
        self.qapplication
        if self.qapplication:
            self.qapplication.quit()
        else:
            print("Aucune instance d'application PyQt6 en cours.")

    def __del__(self):
        """
        Méthode de nettoyage pour libérer les ressources.
        """
        print("SimulationMoves détruite.")
        self.timer.stop()
        if self.qapplication:
            self.qapplication.quit()
        else:
            print("Aucune instance d'application PyQt6 en cours.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    algorithm = HanoiIterative(5)  # Nombre de palets fixé à 5
    window = SimulationMoves(algorithm)
    window.show()
    sys.exit(app.exec())
