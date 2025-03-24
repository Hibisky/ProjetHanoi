import time

from PyQt6.QtWidgets import QApplication, QInputDialog

from BlocVision.CameraProcessor import CameraProcessor


class DetectionInterface:
    """
    Interface utilisateur avec PyQt6 pour afficher le nombre de palets détectés
    et permettre la validation ou modification.
    """

    def __init__(self, detected_count):
        self.detected_count = detected_count
        self.validated_count = None

    def show_interface(self):
        """
        Affiche une boîte de dialogue permettant à l'utilisateur de valider ou modifier le nombre de palets détectés.
        """
        app = QApplication([])  # Création de l'application PyQt6

        user_input, ok = QInputDialog.getInt(
            None,
            "Validation",
            f"Nombre de palets détectés : {self.detected_count}\n"
            "Confirmez ou entrez le nombre correct :",
            min=self.detected_count,
        )

        if ok:
            self.validated_count = user_input
        else:
            self.validated_count = self.detected_count

        print(f"Nombre de palets validé par l'utilisateur : {self.validated_count}")
        return self.validated_count


if __name__ == "__main__":
    processor = CameraProcessor()
    frame = processor.capture_image()
    print(f"Capture image")
    if frame is not None:
        detection_id = int(time.time())
        num_discs, _ = processor.detect_discs(frame, detection_id)
        print(f"Nombre de palets détectés : {num_discs}")

        interface = DetectionInterface(num_discs)
        validated_count = interface.show_interface()
