import sys
from PyQt6.QtWidgets import QApplication
import time
import threading
from BlocAlgo.HanoiIterative import HanoiIterative
from BlocAlgo.SimulationMoves import SimulationMoves
from BlocVision.CameraProcessor import CameraProcessor
from BlocVision.DetectionInterface import DetectionInterface
from BlocRobot.DobotControl import DobotControl
import signal

def main():
    """
    Programme principal pour résoudre la Tour de Hanoï avec un robot et une caméra.
    """

    print("Program Start:")
    
    # === 1. INITIALISATION DES COMPOSANTS === 
    print("Initialisation du robot...")
    robot = DobotControl()  # Création de l'instance du robot
    robot.execute_init()

    print("Initialisation de la caméra...")
    robot.move_to_and_check(220, -100, 155)
    processor = CameraProcessor()

    print("Initialisation de l'interface...")
    interface = DetectionInterface()

    # === 2. ACQUISITION DE L'ÉTAT INITIAL ===
    print("Prise de photo pour analyser la tour d'origine...")
    frame = processor.capture_image()

    if frame is not None:
        detection_id = int(time.time())
        num_discs, _ = processor.detect_discs(frame, detection_id)
        print(f"Nombre de palets détectés : {num_discs}")
    
    #On valide mtn le nombre de palets par l'utilisateur 
    #interface = DetectionInterface(num_discs)
    validated_count = interface.run_detection_workflow()


    # === 3. CALCUL DES DÉPLACEMENTS SELON L'ALGORITHME DE HANOÏ ===
    print("Calcul des déplacements...")
    algo = HanoiIterative(validated_count)# Génération de la liste des déplacements

    # === 4. EXECUTION DES DEPLACEMENTS PAR LA SIMULATION ===
    app = QApplication(sys.argv)
    simulation = SimulationMoves(algo)
    simulation.show()

    # === 4. EXÉCUTION DES DÉPLACEMENTS PAR LE ROBOT ===

    for coup, origine, destination, palets_origin_before, palets_destination_before in algo.get_move_matrix():
        print(f"Exécution du déplacement {coup}: {origine} -> {destination}")
        robot.realiser_deplacement(origine, destination, palets_origin_before, palets_destination_before)
        
    print("Résolution de la Tour de Hanoï terminée !")
    robot.return_to_home()
    robot.disconnect()

    # === 5.FIN DU PROGRAMME ===

    print("Program End.")
    sys.exit(app.exec())
    exit(0)

def signal_handler(sig, frame):
    """
    Gestionnaire pour les signaux système (ex. Ctrl + C).
    """
    print("\n🔴 Interruption reçue. Arrêt du programme...")
    sys.exit(0)

def __del__():
    """
    Méthode de nettoyage pour libérer les ressources.
    """
    # Arrêter le main
    print("Arrêt du programme...")
    sys.exit(0)

if __name__ == "__main__":
    # Capture des signaux système (ex. Ctrl + C)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
    sys.exit(0)
    
#TODO: robot: Commentaires !

#TODO: vision: retirer le bruit sur les images
#TODO: vision: methode deconnexion camera
    
#TODO: interface: methode deconnexion interface
#TODO: interface: ajouter la simulation à l'interface NOT NECESSARY

#TODO: DOC: Planning réel
#TODO: DOC: Slides Soutenance
#TODO: README: Update du readme