#!/usr/bin/env python

import time
import threading
from serial.tools import list_ports
import pydobot
from pydobot.message import Message
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs
import sys
from BlocAlgo.HanoiIterative import HanoiIterative
from BlocRobot.Filter_pydobot import FilterPydobotLogs
import BlocRobot.DobotCalibrate as DobotCalibrator
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

H_PALET0   = -82
H_PALET1   = -55 
H_PALET2   = -30 
H_PALET3   = -5 
H_PALET4   = 20 
H_PALET5   = 45
AXE_DROITE = 150
AXE_GAUCHE = -150
AXE_CENTRE = 0
H_BRAS_LEVE = 155
DIST_COLONNES = 220


class DobotControl:
    """
    Classe pour contrôler le robot Dobot.
    """
    
    def __init__(self, home_x=220, home_y=-7, home_z=100):
        """
        Initialise le DobotControl avec les coordonnées de la position de départ.
        :param home_x: Coordonnée x de la position de départ.
        :param home_y: Coordonnée y de la position de départ.
        :param home_z: Coordonnée z de la position de départ.
        """
        self.connected = False
        self.device = None
        self.ERROR_NOT_CONNECTED = "Le Dobot n'est pas connecte."
        self.ERROR_INVALID_PALLET_COUNT = "Nombre de palets invalide"
        available_ports = list_ports.comports()
        if not available_ports:
            raise RuntimeError("Aucun port disponible pour connecter le Dobot.")
        print(f'available ports: {[x.device for x in available_ports]}')

        self.port = None
        timeout = 5  # Timeout de 10 secondes pour la connexion
        for port in available_ports:
            try:
                print(f"Test de connexion au port : {port.device}")
                # Essayez d'initialiser le Dobot sur ce port
                test_device = self.try_connect_dobot(port, timeout=timeout)
                test_device.close()  # Si la connexion réussit, fermez-la immédiatement
                self.port = port.device
                print(f"✅ Port valide trouvé : {self.port}")
                break
            except RuntimeError as e:
                print(f"❌ Échec de connexion au port {port.device}: Timeout dépassé")  # Timeout atteint pour ce port
            except Exception as e:
                print(f"❌ Échec de connexion au port {port.device}")

        if self.port is None:
            raise RuntimeError("Aucun port USB série valide trouvé pour le Dobot.")
        else:
            # Initialisez le Dobot avec le port trouvé
            sys.stdout = FilterPydobotLogs(sys.stdout)
            self.device = pydobot.Dobot(port=self.port, verbose=True)
            self.connected = True
            time.sleep(1) # Attendre que le Dobot soit prêt
        # Cible initiale
        self.home_x = home_x
        self.home_y = home_y
        self.home_z = home_z
        self.cible_x = DIST_COLONNES
        self.cible_y = 0
        self.cible_z = 0
        self.CALIB_Y = 0
        self.CALIB_Z = 0

        # Patch si la méthode n'existe pas
        if not hasattr(self.device, 'home'):
            print("Ajout de la méthode home au Dobot")
            self._patch_home()
        
        # Va à la position home
        print("Déplacement vers la position home...")
        self.device.home()
        
        # Se repositionner à home après calibration
        print("Repositionnement à la position home...")
        self.move_to_and_check(self.home_x, self.home_y, self.home_z)
        self.device.move_to(home_x, home_y, home_z, 0, True)

    def try_connect_dobot(self, port, timeout=5):
        """
        Tente de se connecter au Dobot sur un port donné avec un timeout.
        :param port: Port série à tester.
        :param timeout: Durée maximale en secondes pour la tentative.
        :return: Instance Dobot si la connexion réussit, sinon lève une exception.
        """
        result = [None]  # Utilisation d'une liste mutable pour stocker le résultat dans le thread
        exception = [None]

        def connect():
            try:
                result[0] = pydobot.Dobot(port=port.device, verbose=False)
            except Exception as e:
                exception[0] = e

        # Lancer la connexion dans un thread séparé
        thread = threading.Thread(target=connect)
        thread.start()
        thread.join(timeout)  # Attendre jusqu'à ce que le thread termine ou que le timeout soit atteint

        if thread.is_alive():
            # Si le thread est toujours actif après le timeout, on lève une exception
            raise RuntimeError(f"⏳ Timeout atteint pour la connexion au port {port.device}.")
        if exception[0]:
            # Si une exception a été levée dans le thread, on la relance
            raise exception[0]

        thread.join()  # Assurez-vous que le thread est terminé avant de continuer
        return result[0]

    def execute_init(self):
        
        #Exécute les mouvements et opérations nécessaires pour chaque position définie.
        try:
            for index in 0,1,2:

                # Mouvement au-dessus de la position
                if(index == 0):
                    self.deplacer_vers_colonne_gauche()
                    self.grab_pallet(5, grab=True)
                    time.sleep(1)
                    self.grab_pallet(4, grab=False)
                if(index == 1):
                    self.deplacer_vers_colonne_centre()
                    # Activer la ventouse pour ramasser
                    self.activate_ventouse(True)
                    time.sleep(1)
                    # Désactiver la ventouse pour déposer
                    self.activate_ventouse(False)

                if(index == 2):
                    self.deplacer_vers_colonne_droite()
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
            self.device.close()
            self.connected = False

    def move_to_and_check(self, x, y, z, r=0, wait=True):
        """
        Déplace le Dobot et vérifie la position.
        """
        self.device.move_to(x, y, z, r, wait)
        time.sleep(0.3)
        
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
        """
        Déplacement vers colonne de gauche.
        :param r: Angle de rotation.
        :param wait: Attendre la fin du mouvement.
        """
        self.cible_x = DIST_COLONNES
        self.cible_y = AXE_GAUCHE
            
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        print(f"Déplacement vers x={self.cible_x}, y={AXE_GAUCHE}, z={self.cible_z}, r={r}")
        self.device.move_to(self.cible_x, self.cible_y, H_BRAS_LEVE, r, wait)

    def deplacer_vers_colonne_centre(self, r=0, wait=True):
        """
        Déplacement vers colonne de centre.
        :param r: Angle de rotation.
        :param wait: Attendre la fin du mouvement.
        """
        self.cible_x = DIST_COLONNES
        self.cible_y = AXE_CENTRE
            
        if not self.connected:
            raise RuntimeError(self.ERROR_NOT_CONNECTED)

        print(f"Déplacement vers x={self.cible_x}, y={AXE_CENTRE}, z={self.cible_z}, r={r}")
        self.device.move_to(self.cible_x, self.cible_y, H_BRAS_LEVE, r, wait)
    
    def deplacer_vers_colonne_droite(self, r=0, wait=True):
        """
        Déplacement vers colonne de droite.
        :param r: Angle de rotation.
        :param wait: Attendre la fin du mouvement.
        """
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
        if threading.current_thread() is not threading.main_thread():
            threading.currentThread().join()
            print("Destruction de l'objet DobotControl.")
        self.connected = False
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
        """
        Déplace le robot verticalement en fonction du nombre de palets.
        """
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

    def _patch_home(self):
        """
        Ajoute une méthode home à l'instance pydobot.Dobot, avec attente de fin de mouvement.
        """
        def dobot_home(_self, timeout=25):
            """
            Déplace le robot à la position home et attend la fin du mouvement.
            :param timeout: Temps d'attente maximum pour le mouvement.
            """
            print("🏠 Exécution de la commande Home (code SET_HOME_CMD)...")
            msg = Message()
            msg.id = CommunicationProtocolIDs.SET_HOME_CMD
            _self._send_command(msg)

            # Attente active que le robot ait terminé (polling)
            start_time = time.time()
            while True:
                if time.time() - start_time > timeout:
                    print("⚠️ Timeout atteint.")
                    break
                time.sleep(0.2)  # petite pause pour éviter de spammer le port série

        self.device.home = dobot_home.__get__(self.device)



if __name__ == "__main__":
    robot = DobotControl()
    print("Phase d'initialisation du robot...")
    robot.execute_init()
    
    print("Phase de résolution de la Tour de Hanoï...")
    hanoi = HanoiIterative(4)  # Initialisation avec 4 disques

    # Boucle pour exécuter les mouvements de la matrice
    for coup, origine, destination, palets_origin_before, palets_destination_before in hanoi.get_move_matrix():
        print(f"Exécution du déplacement {coup}: {origine} -> {destination}")
        robot.realiser_deplacement(origine, destination, palets_origin_before, palets_destination_before)