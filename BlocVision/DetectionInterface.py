import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QCheckBox, QPushButton, QVBoxLayout,
    QLabel, QInputDialog
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox
import numpy as np

from CameraProcessor import CameraProcessor
import time

class InitialConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuration initiale")

        self.config_confirmed = False
        self.save_images_checkbox = QCheckBox("Enregistrer les images")
        self.show_images_checkbox = QCheckBox("Afficher les images à l'écran")
        self.launch_button = QPushButton("Lancer")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sélectionnez les options avant de démarrer :"))
        layout.addWidget(self.save_images_checkbox)
        layout.addWidget(self.show_images_checkbox)
        layout.addWidget(self.launch_button)

        self.setLayout(layout)

        self.launch_button.clicked.connect(self.on_launch)

        self.save_images = False
        self.show_images = False

    def on_launch(self):
        self.save_images = self.save_images_checkbox.isChecked()
        self.show_images = self.show_images_checkbox.isChecked()
        self.config_confirmed = True
        self.close()

class MultiImageViewer(QWidget):
    def __init__(self, images: list[tuple[str, np.ndarray]]):
        super().__init__()
        self.setWindowTitle("Visualisation des étapes")
        self.images = images
        self.index = 0

        self.image_label = QLabel()
        self.title_label = QLabel()
        self.next_button = QPushButton("→")

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_button.clicked.connect(self.next_image)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.display_image(0)

    def display_image(self, index):
        title, image_np = self.images[index]
        height, width, channel = image_np.shape
        bytes_per_line = 3 * width
        q_img = QImage(image_np.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)

        self.title_label.setText(title)
        self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio))

    def next_image(self):
        self.index += 1
        if self.index < len(self.images):
            self.display_image(self.index)
        else:
            self.close()

class DetectionInterface:
    def __init__(self):
        self.detected_count = 0
        self.validated_count = 0
        self.save_images = False
        self.show_images = False

    def show_cancel_message(self, message="Action annulée par l'utilisateur."):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        QMessageBox.information(None, "Annulation", message)

    def show_initial_config(self):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        config_window = InitialConfigWindow()
        config_window.show()
        app.exec()

        if not config_window.config_confirmed:
            self.show_cancel_message("Configuration annulée par l'utilisateur.")
            raise RuntimeError("Configuration annulée.")

        self.save_images = config_window.save_images
        self.show_images = config_window.show_images

        
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


    def show_image_steps(self, images):
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        viewer = MultiImageViewer(images)
        viewer.show()
        app.exec()

    def run_detection_workflow(self, image_path: str = None):
        self.show_initial_config()

        processor = CameraProcessor(save_images=self.save_images, show_images=self.show_images)
        if image_path:
            frame = processor.load_image_from_file(image_path)
        else:
            frame = processor.capture_image()


        if frame is not None:
            detection_id = int(time.time())
            num_discs, steps = processor.detect_discs(frame, detection_id)
            self.detected_count = num_discs

            if self.show_images:
                self.show_image_steps(steps)

            self.show_validation_dialog()
        else:
            print("Erreur lors de la capture d’image.")


if __name__ == "__main__":
    image_path = "/Users/boblabrike/Desktop/step_0_raw.png"
    interface = DetectionInterface()
    interface.run_detection_workflow(image_path=image_path)
