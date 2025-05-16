import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QCheckBox, QPushButton, QVBoxLayout,
    QLabel, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import numpy as np
import time

from CameraProcessor import CameraProcessor  # Classe de traitement d'image

# Fenêtre de configuration initiale (affichage et sauvegarde d'images)
class InitialConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration initiale")

        # État de validation de la configuration
        self.config_confirmed = False

        # Cases à cocher pour les options utilisateur
        self.save_images_checkbox = QCheckBox("Enregistrer les images")
        self.show_images_checkbox = QCheckBox("Afficher les images à l'écran")
        self.launch_button = QPushButton("Lancer")

        # Mise en page verticale
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sélectionnez les options avant de démarrer :"))
        layout.addWidget(self.save_images_checkbox)
        layout.addWidget(self.show_images_checkbox)
        layout.addWidget(self.launch_button)

        self.setLayout(layout)

        # Connexion du bouton à la méthode de validation
        self.launch_button.clicked.connect(self.on_launch)

        self.save_images = False
        self.show_images = False

    # Méthode appelée quand l'utilisateur clique sur "Lancer"
    def on_launch(self):
        self.save_images = self.save_images_checkbox.isChecked()
        self.show_images = self.show_images_checkbox.isChecked()
        self.config_confirmed = True
        self.close()


# Fenêtre de visualisation des différentes étapes d'image
class MultiImageViewer(QWidget):
    def __init__(self, images: list[tuple[str, np.ndarray]]):
        super().__init__()
        self.setWindowTitle("Visualisation des étapes")
        self.images = images
        self.index = 0  # Index de l'image affichée

        # Widgets
        self.image_label = QLabel()
        self.title_label = QLabel()
        self.next_button = QPushButton("→")

        # Alignement
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connexion au bouton "suivant"
        self.next_button.clicked.connect(self.next_image)

        # Mise en page
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.display_image(0)  # Affiche la première image

    # Affiche une image à un index donné
    def display_image(self, index):
        title, image_np = self.images[index]
        height, width, channel = image_np.shape
        bytes_per_line = 3 * width

        # Conversion en image Qt
        q_img = QImage(image_np.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)

        # Mise à jour des widgets
        self.title_label.setText(title)
        self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio))

    # Affiche l'image suivante ou ferme si terminé
    def next_image(self):
        self.index += 1
        if self.index < len(self.images):
            self.display_image(self.index)
        else:
            self.close()


# Interface principale de détection
class DetectionInterface:
    def __init__(self):
        self.detected_count = 0     # Nombre de palets détectés
        self.validated_count = 0    # Nombre de palets validés par l'utilisateur
        self.save_images = False
        self.show_images = False
        self.processor = None       # Instance de CameraProcessor

    # Méthode appelée à la destruction de l'objet (nettoyage)
    def __del__(self):
        print("Interface de détection détruite.")
        if self.processor:
            del self.processor

    # Affiche un message d’annulation
    def show_cancel_message(self, message="Action annulée par l'utilisateur."):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        QMessageBox.information(None, "Annulation", message)

    # Affiche la fenêtre de configuration initiale
    def show_initial_config(self):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        config_window = InitialConfigWindow()
        config_window.show()
        app.exec()  # Bloc jusqu'à fermeture

        if not config_window.config_confirmed:
            self.show_cancel_message("Configuration annulée par l'utilisateur.")
            raise RuntimeError("Configuration annulée.")

        # Récupération des options utilisateur
        self.save_images = config_window.save_images
        self.show_images = config_window.show_images

    # Affiche une boîte de dialogue pour valider le nombre de palets
    def show_validation_dialog(self):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        user_input, ok = QInputDialog.getInt(
            None, "Validation",
            f"Nombre de palets détectés : {self.detected_count}\n"
            "Confirmez ou entrez le nombre correct :",
            min=self.detected_count
        )

        if ok:
            self.validated_count = user_input
        else:
            QMessageBox.information(
                None,
                "Annulation",
                "Validation annulée par l'utilisateur."
            )
            raise RuntimeError("Validation annulée.")

        print(f"Nombre de palets validé par l'utilisateur : {self.validated_count}")
        return self.validated_count

    # Affiche les étapes du traitement d’image
    def show_image_steps(self, images):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        viewer = MultiImageViewer(images)
        viewer.show()
        app.exec()

    # Méthode principale : exécute tout le processus de détection
    def run_detection_workflow(self, image_path: str = None):
        self.show_initial_config()  # Configuration utilisateur

        self.processor = CameraProcessor(save_images=self.save_images, show_images=self.show_images)

        # Chargement ou capture d'image
        if image_path:
            frame = self.processor.load_image_from_file(image_path)
        else:
            frame = self.processor.capture_image()

        # Détection et affichage des résultats
        if frame is not None:
            detection_id = int(time.time())
            num_discs, steps = self.processor.detect_discs(frame, detection_id)
            self.detected_count = num_discs

            if self.show_images:
                self.show_image_steps(steps)

            validated_count = self.show_validation_dialog()
            return validated_count
        else:
            print("Erreur lors de la capture d’image.")


# Point d'entrée principal du script
if __name__ == "__main__":
    image_path = "detections/detection_1742838667/step_0_raw.png"
    interface = DetectionInterface()
    interface.run_detection_workflow()
