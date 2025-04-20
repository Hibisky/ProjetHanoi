import cv2
import numpy as np
import time
import os

# Paramètres pour le traitement des palets
CIRCULARITY_MIN = 0.8
AREA_MIN = 100
MIN_DISTANCE = 2

class CameraProcessor:
    def __init__(self, camera_index=0, save_images=False, show_images=False):
        self.camera_index = camera_index
        self.save_images = save_images
        self.show_images = show_images

        
    def load_image_from_file(self, path):
        frame = cv2.imread(path)
        if frame is None or not np.any(frame):
            print(f"Erreur : impossible de charger l’image depuis {path}")
            return None
        return frame

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
        return frame if np.any(frame) else None

    def detect_discs(self, frame, detection_id):
        folder_name = f"detections/detection_{detection_id}"
        os.makedirs(folder_name, exist_ok=True)

        steps_to_display = []

        # Étape 0 : brute
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_0_raw.png"), frame)
        steps_to_display.append(("Image brute", frame.copy()))

        # Étape 1 : gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_1_gray.png"), gray)
        steps_to_display.append(("Gris", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)))

        # Étape 2 : flou
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_2_blur.png"), blurred)
        steps_to_display.append(("Flou", cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)))

        # Étape 3 : seuillage adaptatif
        thresholded = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV, 21, 10
        )
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_3_threshold.png"), thresholded)
        steps_to_display.append(("Seuillage", cv2.cvtColor(thresholded, cv2.COLOR_GRAY2BGR)))

        # Étape 4 : fermeture morphologique
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, kernel)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_4_closed.png"), closed)
        steps_to_display.append(("Fermeture morphologique", cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)))

        # Étape 5 : contours
        contours, _ = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        contour_frame = frame.copy()
        cv2.drawContours(contour_frame, contours, -1, (0, 255, 0), 2)
        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_5_contours.png"), contour_frame)
        steps_to_display.append(("Contours initiaux", contour_frame.copy()))

        # Étape 6 : filtrage par circularité et aire
        valid_contours = []
        for contour in contours:
            if self.classify_contour(contour):
                (x, y), radius = cv2.minEnclosingCircle(contour)
                valid_contours.append(((int(x), int(y)), int(radius), contour))

        # Étape 7 : suppression des doublons
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
            cv2.putText(final_frame, f"R: {radius}", (center[0]+10, center[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        if self.save_images:
            cv2.imwrite(os.path.join(folder_name, "step_6_validated_contours.png"), final_frame)
        steps_to_display.append(("Contours validés", final_frame.copy()))

        palets = sorted(palets, key=lambda d: d[0])
        return len(palets), steps_to_display

    def classify_contour(self, contour):
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if area < AREA_MIN or perimeter == 0:
            return False
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        return circularity > CIRCULARITY_MIN


if __name__ == "__main__":
    processor = CameraProcessor()
    frame = processor.load_image_from_file("/Users/boblabrike/Desktop/step_0_raw.png")

    if frame is not None:
        detection_id = int(time.time())
        num_discs, _ = processor.detect_discs(frame, detection_id)
        print(f"Nombre de palets détectés : {num_discs}")
