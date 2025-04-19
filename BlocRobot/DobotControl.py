#!/usr/bin/env python

import time
from serial.tools import list_ports
import pydobot
import sys
from BlocAlgo.HanoiIterative import HanoiIterative
from BlocRobot.Filter_pydobot import FilterPydobotLogs

H_PALET0   = -75 #-5
H_PALET1   = -50 #-5
H_PALET2   = -25 #-5
H_PALET3   = 0 #-5
H_PALET4   = 25 #+5
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

        self.port = next((p.device for p in available_ports if "usbserial" in p.device or "usbmodem" in p.device), None)
        if self.port is None:
            raise RuntimeError("Aucun port USB série valide trouvé pour le Dobot.")
        #print(f"Connexion au port : {self.port}")
        # Appliquer le filtre avant d'initialiser pydobot
        sys.stdout = FilterPydobotLogs(sys.stdout)
        self.device = pydobot.Dobot(port=self.port, verbose=True)
        self.connected = True
        self.home_x = home_x
        self.home_y = home_y
        self.home_z = home_z
        self.cible_x = DIST_COLONNES
        self.cible_y = 0
        self.cible_z = 0
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
        print(f"palets à saisir : {nb_palet}")
        #Saisir un palet.
        if(grab == False):
            nb_palet += 1;  # Ajout du palet à déposer
        self.move_vertical_switch(nb_palet)

        print(f"Position actuelle : x={self.cible_x}, y={self.cible_y}, z={self.cible_z}, r={r}")

        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)
        self.device.move_to(self.cible_x, self.cible_y, self.cible_z, r, wait)
        self.activate_ventouse(grab)
        if grab:
            print("Palet saisi")
        else:
            print("Palet déposé")
        self.device.move_to(self.cible_x, self.cible_y, 150, r, wait)

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
        self.deplacer_vers_axe(origine)
        self.grab_pallet(palets_origin_before, grab=True)
        self.deplacer_vers_axe(destination)
        self.grab_pallet(palets_destination_before, grab=False)

    def move_vertical_switch(self, nb_palet):
        match nb_palet:
            case 0:
                print(f"H= {H_PALET0}")
                self.cible_z = H_PALET0
            case 1:
                print(f"H= {H_PALET1}")
                self.cible_z = H_PALET1
            case 2:
                print(f"H= {H_PALET2}")
                self.cible_z = H_PALET2
            case 3:
                print(f"H= {H_PALET3}")
                self.cible_z = H_PALET3
            case 4:
                print(f"H= {H_PALET4}")
                self.cible_z = H_PALET4
            case 5:
                print(f"H= {H_PALET5}")
                self.cible_z = H_PALET5
            case _:
                raise ValueError(self.ERROR_INVALID_PALLET_COUNT)


if __name__ == "__main__":
    robot = DobotControl()
    print(f"Phase d'initialisation du robot...")
    robot.execute_init()
    
    print(f"Phase de résolution de la Tour de Hanoï...")
    hanoi = HanoiIterative(4)  # Initialisation avec 4 disques

    # Boucle pour exécuter les mouvements de la matrice
    for coup, origine, destination, palets_origin_before, palets_destination_before in hanoi.get_move_matrix():
        print(f"Exécution du déplacement {coup}: {origine} -> {destination}")
        robot.realiser_deplacement(origine, destination, palets_origin_before, palets_destination_before)