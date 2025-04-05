import cv2
import numpy as np
import time
import os

# Paramètres pour le traitement des palets
CIRCULARITY_MIN = 0.8   # Seuil de circularité pour considérer une forme comme un palet
AREA_MIN = 100          # Taille minimale d'un palet pour éviter les faux positifs
MIN_DISTANCE = 2       # Distance minimale entre deux palets pour éviter les doublons

class CameraProcessor:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index

    def capture_image(self):
        cap = cv2.VideoCapture(self.camera_index)
        time.sleep(1)

        frame = None
        for _ in range(5):
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Erreur : Impossible de capturer une image valide.")
                cap.release()
                return None

        cap.release()

        if not np.any(frame):
            print("Erreur : L'image capturée est vide ou noire.")
            return None
    
        return frame

    def detect_discs(self, frame, detection_id):
        folder_name = f"detections/detection_{detection_id}"
        os.makedirs(folder_name, exist_ok=True)
        
        # Étape 0 : brute
        cv2.imwrite(os.path.join(folder_name, "step_0_raw.png"), frame)

        # Étape 1 : gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.join(folder_name, "step_1_gray.png"), gray)

        # Étape 2 : flou
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        cv2.imwrite(os.path.join(folder_name, "step_2_blur.png"), blurred)

        # Étape 3 : seuillage adaptatif
        thresholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY_INV, 21, 10)
        cv2.imwrite(os.path.join(folder_name, "step_3_threshold.png"), thresholded)

        # Étape 4 : fermeture morphologique
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite(os.path.join(folder_name, "step_4_closed.png"), closed)

        # Étape 5 : contours
        contours, _ = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        contour_frame = frame.copy()
        cv2.drawContours(contour_frame, contours, -1, (0, 255, 0), 2)
        cv2.imwrite(os.path.join(folder_name, "step_5_contours.png"), contour_frame)

        # Étape 6 : filtrage par circularité et aire
        valid_contours = []
        for contour in contours:
            if self.classify_contour(contour):
                (x, y), radius = cv2.minEnclosingCircle(contour)
                valid_contours.append(((int(x), int(y)), int(radius), contour))

        # Étape 7 : suppression des doublons (centres trop proches)
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

        # Étape 8 : dessin final
        final_frame = frame.copy()
        palets = []
        for center, radius, contour in filtered:
            palets.append((radius, center))
            cv2.drawContours(final_frame, [contour], -1, (0, 255, 0), 2)
            cv2.circle(final_frame, center, 5, (255, 0, 0), -1)

        cv2.imwrite(os.path.join(folder_name, "step_6_validated_contours.png"), final_frame)

        palets = sorted(palets, key=lambda d: d[0])
        return len(palets), palets

    def classify_contour(self, contour):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if area < AREA_MIN or perimeter == 0:
            return False
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        return circularity > CIRCULARITY_MIN

if __name__ == "__main__":
    processor = CameraProcessor()
    frame = processor.capture_image()
    if frame is not None:
        detection_id = int(time.time())
        num_discs, discs = processor.detect_discs(frame, detection_id)
        print(f"Nombre de palets détectés : {num_discs}")