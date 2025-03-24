#!/usr/bin/env python

import time
from serial.tools import list_ports
import pydobot
import sys
from BlocAlgo.HanoiIterative import HanoiIterative
from BlocRobot.Filter_pydobot import FilterPydobotLogs
import DobotCalibrate as DobotCalibrator
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

H_PALET0   = -80
H_PALET1   = -55
H_PALET2   = -30
H_PALET3   = -5
H_PALET4   = 20
H_PALET5   = 50
AXE_DROITE = 150
AXE_GAUCHE = -150
AXE_CENTRE = 0
H_BRAS_LEVE = 150
DIST_COLONNES = 220
class DobotControl:
    
    def __init__(self, home_x=220, home_y=0, home_z=100):
        #Initialise le contrôle Dobot.
        self.ERROR_NOT_CONNECTED = "Le Dobot n'est pas connecte."
        self.ERROR_INVALID_PALLET_COUNT = "Nombre de palets invalide"
        available_ports = list_ports.comports()
        if not available_ports:
            raise RuntimeError("Aucun port disponible pour connecter le Dobot.")
        print(f'available ports: {[x.device for x in available_ports]}')

        self.port = available_ports[4].device  # Choisir le port approprié
        print(f"Connexion au port : {self.port}")
        # Appliquer le filtre avant d'initialiser pydobot
        sys.stdout = FilterPydobotLogs(sys.stdout)
        self.device = pydobot.Dobot(port=self.port, verbose=True)
        self.connected = True
        # Cible initiale
        self.home_x = home_x
        self.home_y = home_y
        self.home_z = home_z
        self.cible_x = DIST_COLONNES
        self.cible_y = 0
        self.cible_z = 0
        self.CALIB_Y = 0
        self.CALIB_Z = 0
        # Va à la position home
        self.device.home()
        #self.calibrer_hauteur()  # Définir une nouvelle référence Z
        
        # Se repositionner à home après calibration
        self.move_to_and_check(self.home_x, self.home_y, self.home_z)
        self.device.move_to(home_x, home_y, home_z, 0, True)

    def execute_init(self):
        
        #Exécute les mouvements et opérations nécessaires pour chaque position définie.
        try:
            for index in 0,1,2:

                # Mouvement au-dessus de la position
                if(index == 0):
                    self.deplacer_vers_colonne_droite()
                    self.grab_pallet(5, grab=True)
                    self.grab_pallet(5, grab=False)
                if(index == 1):
                    self.deplacer_vers_colonne_centre(0)
                    # Activer la ventouse pour ramasser
                    self.activate_ventouse(True)
                    time.sleep(1)
                    # Désactiver la ventouse pour déposer
                    self.activate_ventouse(False)

                if(index == 2):
                    self.deplacer_vers_colonne_gauche(0)
                    # Activer la ventouse pour ramasser
                    self.activate_ventouse(True)
                    time.sleep(1)
                    # Désactiver la ventouse pour déposer
                    self.activate_ventouse(False)

            # Retour au point de départ
            print("Retour au point de départ.")
            self.return_to_home()

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def calibrer_hauteur(self, step=5):
        """
        Descend progressivement jusqu'à toucher une surface pour calibrer le Z.
        """
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        print("Début de la calibration en Z...")

        pose = self.get_pose()
        current_z = pose[2]

        while current_z > -100:  # Limite de sécurité
            self.device.move_to(pose[0], pose[1], current_z - step, 0, True)
            time.sleep(0.2)  # Laisser le temps au mouvement
            
            new_pose = self.get_pose()
            current_z = new_pose[2]
            
            if self.detect_contact():
                print(f"Contact détecté à Z={current_z}. Réglage de la référence.")
                self.home_z = current_z
                return
        
        print("Aucune surface détectée dans la plage définie.")

    def detect_contact(self):
        """
        Détecte le contact avec une surface.
        """
        pose = self.get_pose()
        return pose[2] < -90  # Seuil ajustable

    def move_to_and_check(self, x, y, z, r=0, wait=True):
        """
        Déplace le Dobot et vérifie la position.
        """
        self.device.move_to(x, y, z, r, wait)
        time.sleep(0.5)
        
        pose = self.get_pose()
        if abs(pose[0] - x) > 2 or abs(pose[1] - y) > 2 or abs(pose[2] - z) > 2:
            print(f"Déplacement incorrect : attendu ({x}, {y}, {z}), obtenu ({pose[0]}, {pose[1]}, {pose[2]})")
        else:
            print("Position correcte.")

    def get_pose(self):
        """
        Obtient la position actuelle du Dobot.
        """
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        return self.device.pose()

    def deplacer_vers_colonne_gauche(self, r=0, wait=True):
        #Déplacement vers une position spécifique.
        self.cible_x = DIST_COLONNES
        self.cible_y = AXE_GAUCHE
            
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        print(f"Déplacement vers x={self.cible_x}, y={AXE_GAUCHE}, z={self.cible_z}, r={r}")
        self.device.move_to(self.cible_x, self.cible_y, H_BRAS_LEVE, r, wait)

    def deplacer_vers_colonne_centre(self, r=0, wait=True):
        #Déplacement vers une position spécifique.
        self.cible_x = DIST_COLONNES
        self.cible_y = AXE_CENTRE
            
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        print(f"Déplacement vers x={self.cible_x}, y={AXE_CENTRE}, z={self.cible_z}, r={r}")
        self.device.move_to(self.cible_x, self.cible_y, H_BRAS_LEVE, r, wait)
    
    def deplacer_vers_colonne_droite(self, r=0, wait=True):
        #Déplacement vers une position spécifique.
        self.cible_x = DIST_COLONNES 
        self.cible_y = AXE_DROITE 
        
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        print(f"Déplacement vers x={self.cible_x}, y={AXE_DROITE}, z={self.cible_z}, r={r}")
        self.device.move_to(self.cible_x, self.cible_y, H_BRAS_LEVE, r, wait)

    def grab_pallet(self, nb_palet, r=0, wait=True, grab=True):
        """
        Saisir ou déposer un palet.
        :param nb_palet: Nombre de palets à saisir ou déposer.
        :param r: Angle de rotation.
        :param wait: Attendre la fin du mouvement.
        :param grab: True pour saisir, False pour déposer.
        """
        print(f"Nombre de palets à saisir : {nb_palet}")
        #Saisir un palet.
        if(grab == False):
            nb_palet += 1;  # Ajout du palet à déposer
        self.move_vertical_switch(nb_palet)

        print(f"Position actuelle : x={self.cible_x}, y={self.cible_y}, z={self.cible_z}, r={r}")

        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)
        self.move_to_and_check(self.cible_x, self.cible_y, self.cible_z, r, wait)
        self.activate_ventouse(grab)
        if grab:
            print("Palet saisi")
        else:
            print("Palet déposé")
        self.move_to_and_check(self.cible_x, self.cible_y, 150, r, wait)

    def activate_ventouse(self, activate=True):
        #Activer ou désactiver la ventouse.
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        self.device.suck(activate)
        print("Ventouse activee" if activate else "Ventouse désactivee")

    def get_pose(self):
        #Obtenir la position actuelle du Dobot.
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        pose = self.device.pose()
        print(f"Position actuelle: x={pose[0]}, y={pose[1]}, z={pose[2]}, r={pose[3]}")
        return pose

    def return_to_home(self):
        #Retour a la position initiale (home).
        print(f"Retour à la position de depart : x={self.home_x}, y={self.home_y}, z={self.home_z}")
        self.device.move_to(self.home_x, AXE_CENTRE, self.home_z, r=0, wait=True) #axe_centre anciennement 0

    def disconnect(self):
        #Deconnexion propre du Dobot.
        if self.connected:
            print("Deconnexion du Dobot.")
            self.device.close()
            self.connected = False

    def __del__(self):
        """Destructeur pour deconnecter proprement."""
        self.disconnect()

    def deplacer_vers_axe(self,axe_id):
        """
        Déplace le robot vers l'axe spécifié.
        axe_id : 1 = gauche, 2 = centre, 3 = droite
        """
        match axe_id:
            case 1:
                self.deplacer_vers_colonne_gauche()
            case 2:
                self.deplacer_vers_colonne_centre()
            case 3:
                self.deplacer_vers_colonne_droite()
            case _:
                print(f"Erreur axe_id")
        
            
    def realiser_deplacement(self, origine , destination, palets_origin_before, palets_destination_before):
        """
        Réalise le déplacement entre deux axes.
        """
        self.deplacer_vers_axe(origine)
        self.grab_pallet(palets_origin_before, grab=True)
        self.deplacer_vers_axe(destination)
        self.grab_pallet(palets_destination_before, grab=False)

    def move_vertical_switch(self, nb_palet):
        match nb_palet:
            case 0:
                print(f"nb palet sur axe 0 \n hauteur = ")
                self.cible_z = H_PALET0
            case 1:
                self.cible_z = H_PALET1
            case 2:
                self.cible_z = H_PALET2
            case 3:
                self.cible_z = H_PALET3
            case 4:
                self.cible_z = H_PALET4
            case 5:
                self.cible_z = H_PALET5
            case _:
                raise ValueError(self.ERROR_INVALID_PALLET_COUNT)
            
    def calibrer_manuellement(self):
        """
        Lance la calibration manuelle du robot.
        """
        app = QApplication(sys.argv)
        window = DobotCalibrator(self)
        window.show()
        self.CALIB_Y = self.cible_y
        self.CALIB_Z = self.cible_z
        sys.exit(app.exec())


if __name__ == "__main__":
    robot = DobotControl()
    robot.calibrer_manuellement()
    print(f"Phase d'initialisation du robot...")
    robot.execute_init()
    
    print(f"Phase de résolution de la Tour de Hanoï...")
    hanoi = HanoiIterative(4)  # Initialisation avec 4 disques

    # Boucle pour exécuter les mouvements de la matrice
    for coup, origine, destination, palets_origin_before, palets_destination_before in hanoi.get_move_matrix():
        print(f"Exécution du déplacement {coup}: {origine} -> {destination}")
        robot.realiser_deplacement(origine, destination, palets_origin_before, palets_destination_before)