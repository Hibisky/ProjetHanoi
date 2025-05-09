import unittest
import numpy as np
import cv2
import os
import shutil
import time
from unittest import mock
from CameraProcessor import CameraProcessor

class TestCameraProcessor(unittest.TestCase):
    def setUp(self):
        # Image blanche avec 2 cercles noirs simulant des palets
        self.image = np.ones((300, 300, 3), dtype=np.uint8) * 255
        cv2.circle(self.image, (75, 150), 30, (0, 0, 0), -1)
        cv2.circle(self.image, (225, 150), 30, (0, 0, 0), -1)
        
        self.processor = CameraProcessor(save_images=False, show_images=False)

    def tearDown(self):
        # Nettoyage de tout dossier "detections" généré pendant les tests
        if os.path.exists("detections"):
            shutil.rmtree("detections")

    def test_load_image_from_file_fail(self):
        # Fichier inexistant : devrait retourner None
        result = self.processor.load_image_from_file("zz_file_does_not_exist.png")
        self.assertIsNone(result)

    def test_load_image_from_file_success(self):
        # Sauvegarde temporaire d'une image valide
        temp_path = "temp_test_image.png"
        cv2.imwrite(temp_path, self.image)

        result = self.processor.load_image_from_file(temp_path)
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, self.image.shape)

        os.remove(temp_path)

    def test_classify_contour_true(self):
        # Contour circulaire détecté sur notre image
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Doit classifier au moins un contour comme valide
        self.assertTrue(any(self.processor.classify_contour(c) for c in contours))

    def test_classify_contour_false(self):
        # Contour très petit ou non circulaire
        blank = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(blank, (10, 10), (12, 12), 255, -1)
        contours, _ = cv2.findContours(blank, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            self.assertFalse(self.processor.classify_contour(c))

    def test_detect_discs(self):
        # Test complet du pipeline de détection
        detection_id = int(time.time())
        num_discs, steps = self.processor.detect_discs(self.image, detection_id)

        self.assertGreaterEqual(num_discs, 2)  # On a bien dessiné 2 palets
        self.assertIsInstance(steps, list)
        self.assertTrue(all(isinstance(step, tuple) and len(step) == 2 for step in steps))

    def test_detect_discs_save_images(self):
        # Active l'enregistrement et vérifie que les fichiers sont bien créés
        self.processor.save_images = True
        detection_id = int(time.time())
        num_discs, _ = self.processor.detect_discs(self.image, detection_id)

        folder_path = f"detections/detection_{detection_id}"
        self.assertTrue(os.path.isdir(folder_path))
        expected_files = [
            "step_0_raw.png", "step_1_gray.png", "step_2_blur.png",
            "step_3_threshold.png", "step_4_closed.png",
            "step_5_contours.png", "step_6_validated_contours.png"
        ]
        for fname in expected_files:
            self.assertTrue(os.path.isfile(os.path.join(folder_path, fname)))

    @mock.patch('cv2.VideoCapture')
    def test_capture_image_mocked(self, mock_video_capture):
        # Simulation de capture caméra (aucun matériel requis)
        mock_cap = mock.Mock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (True, self.image)
        mock_cap.isOpened.return_value = True

        frame = self.processor.capture_image()
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, self.image.shape)


if __name__ == '__main__':
    unittest.main()
