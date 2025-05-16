import cv2
import numpy as np
import time
import os

# Seuils utilisés pour filtrer les contours détectés
CIRCULARITY_MIN = 0.8  # Seuil de circularité minimum pour considérer un contour comme un disque
AREA_MIN = 100         # Aire minimale d’un contour
MIN_DISTANCE = 2       # Distance minimale entre deux disques pour éviter les doublons

class CameraProcessor:
    """
    Classe responsable de capturer ou charger des images,
    puis d'effectuer le traitement pour détecter les disques (palets).
    """
    def __init__(self, camera_index=0, save_images=False, show_images=False):
        self.camera_index = camera_index      # Index de la caméra à utiliser
        self.save_images = save_images        # Indique si les étapes doivent être sauvegardées en PNG
        self.show_images = show_images        # Indique si les étapes doivent être affichées (option future)
        self.cap = None                       # Objet VideoCapture de OpenCV

    def __del__(self):
        """
        Libère automatiquement la caméra si elle est encore ouverte.
        """
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            print("Ressource caméra libérée via __del__")

    def load_image_from_file(self, path):
        """
        Charge une image depuis un fichier.
        """
        frame = cv2.imread(path)
        if frame is None or not np.any(frame):
            print(f"Erreur : impossible de charger l’image depuis {path}")
            return None
        return frame

    def capture_image(self):
        """
        Capture une image depuis la caméra après un court délai.
        Retourne un frame valide ou None en cas d'échec.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        time.sleep(1)  # Laisse le temps à la caméra de démarrer

        frame = None
        for _ in range(5):  # Prend quelques frames pour laisser le capteur se stabiliser
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("Erreur : Impossible de capturer une image valide.")
                self.cap.release()
                self.cap = None
                return None

        self.cap.release()
        self.cap = None
        return frame if np.any(frame) else None

    def detect_discs(self, frame, detection_id):
        """
        Applique plusieurs étapes de traitement d’image pour détecter les palets circulaires.
        Retourne le nombre de disques détectés et une liste des étapes visuelles.
        """
        folder_name = f"detections/detection_{detection_id}"
        os.makedirs(folder_name, exist_ok=True)

        steps_to_display = []

        # Étape 0 : Image brute
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_0_raw.png"), frame)
        steps_to_display.append(("Image brute", frame.copy()))

        # Étape 1 : Conversion en niveaux de gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_1_gray.png"), gray)
        steps_to_display.append(("Gris", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)))

        # Étape 2 : Flou gaussien pour réduire le bruit
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_2_blur.png"), blurred)
        steps_to_display.append(("Flou", cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)))

        # Étape 3 : Seuillage adaptatif
        thresholded = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV, 21, 10
        )
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_3_threshold.png"), thresholded)
        steps_to_display.append(("Seuillage", cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)))

        # Étape 4 : Fermeture morphologique (combler les trous)
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_4_closed.png"), closed)
        steps_to_display.append(("Fermeture morphologique", cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)))

        # Étape 5 : Détection des contours
        contours, _ = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        contour_frame = frame.copy()
        cv2.drawContours(contour_frame, contours, -1, (0, 255, 0), 2)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_5_contours.png"), contour_frame)
        steps_to_display.append(("Contours initiaux", contour_frame.copy()))

        # Étape 6 : Filtrage des contours selon circularité et surface
        valid_contours = []
        for contour in contours:
            if self.classify_contour(contour):
                (x, y), radius = cv2.minEnclosingCircle(contour)
                valid_contours.append(((int(x), int(y)), int(radius), contour))

        # Étape 7 : Suppression des doublons (contours trop proches)
        filtered = []
        for center_i, radius_i, contour_i in valid_contours:
            too_close = False
            for center_j, _, _ in filtered:
                dist = np.linalg.norm(np.array(center_i) - np.array(center_j))
                if dist < MIN_DISTANCE:
                    too_close = True
                    break
            if not too_close:
                filtered.append((center_i, radius_i, contour_i))

        # Étape 8 : Affichage final
        final_frame = frame.copy()
        palets = []
        for center, radius, contour in filtered:
            palets.append((radius, center))
            cv2.drawContours(final_frame, [contour], -1, (0, 255, 0), 2)
            cv2.circle(final_frame, center, 5, (255, 0, 0), -1)
            cv2.putText(final_frame, f"R: {radius}", (center[0]+10, center[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_6_validated_contours.png"), final_frame)
        steps_to_display.append(("Contours validés", final_frame.copy()))

        # Trie les disques du plus petit au plus grand rayon
        palets = sorted(palets, key=lambda d: d[0])
        return len(palets), steps_to_display

    def classify_contour(self, contour):
        """
        Vérifie si un contour est suffisamment circulaire et grand pour être considéré comme un palet.
        """
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if area < AREA_MIN or perimeter == 0:
            return False
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        return circularity > CIRCULARITY_MIN


# Si ce fichier est exécuté directement, il lance une détection simple à partir d'une image disque
if __name__ == "__main__":
    processor = CameraProcessor()
    frame = processor.load_image_from_file("/Users/boblabrike/Desktop/step_0_raw.png")

    if frame is not None:
        detection_id = int(time.time())
        num_discs, _ = processor.detect_discs(frame, detection_id)
        print(f"Nombre de palets détectés : {num_discs}")
