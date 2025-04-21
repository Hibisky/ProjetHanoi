from BlocRobot.DobotControl import DobotControl
import time
from serial.tools import list_ports
import pydobot

def send_home_command(device, timeout=10):
    print("🔁 Envoi de la commande 'home' (31)...")
    device._send_command(31)

    print("⏳ Attente du retour à la position d'origine...")
    start = time.time()
    while time.time() - start < timeout:
        pose = device.pose()
        print(f"📍 Position actuelle : x={pose[0]:.2f}, y={pose[1]:.2f}, z={pose[2]:.2f}")
        time.sleep(0.5)
    print("✅ Fin du test de mouvement Home (vérifie le mouvement réel).")


class TestRobot:

    def test_grab_pallet(self):
        robot = DobotControl()
        robot.execute_init()
        robot.grab_pallet(1, grab=True)
        robot.grab_pallet(1, grab=False)
        robot.return_to_home()
        robot.disconnect()

    def test_move_to(self):
        robot = DobotControl()
        robot.execute_init()
        robot.move_to(200, 200, 150, 0, wait=True)
        robot.return_to_home()
        robot.disconnect()
    
    def test_move_to_colonne(self):
        robot = DobotControl()
        robot.execute_init()    
        robot.deplacer_vers_axe(1)
        robot.deplacer_vers_axe(2)
        robot.deplacer_vers_axe(3)
        robot.return_to_home()
        robot.disconnect()

    def test_hauteur(self):
        print("Test de la hauteur du robot")
        print("🔎 Recherche de ports disponibles...")
        robot = DobotControl()
        try:
            print("🔄 Déplacement vers la colonne de droite hauteur 1 pallet")
            robot.deplacer_vers_colonne_droite()
            robot.grab_pallet(1, grab=True)
            robot.activate_ventouse(False)
            print("🔄 Déplacement vers la colonne de droite hauteur 2 pallets")
            robot.deplacer_vers_colonne_droite()
            robot.grab_pallet(2, grab=True)
            robot.activate_ventouse(False)
            print("🔄 Déplacement vers la colonne de droite hauteur 3 pallets")
            robot.deplacer_vers_colonne_droite()
            robot.grab_pallet(3, grab=True)
            robot.activate_ventouse(False)
            print("🔄 Déplacement vers la colonne de droite hauteur 4 pallets")
            robot.deplacer_vers_colonne_droite()
            robot.grab_pallet(4, grab=True)
            robot.activate_ventouse(False)
            print("🔄 Déplacement vers la colonne de droite hauteur 5 pallets")
            robot.deplacer_vers_colonne_droite()
            robot.grab_pallet(5, grab=True)
            robot.activate_ventouse(True)
            print("🔄 Déplacement vers la colonne de droite hauteur 0 pallets, dépose du palet")
            robot.deplacer_vers_colonne_droite()
            robot.grab_pallet(0, grab=False)

        except Exception as e:
                print(f"⚠️ Erreur lors du test : {e}")
        finally:
            print("🔌 Déconnexion...")
            robot.disconnect()
        print("✅ Test de la hauteur terminé.")

    def test_home(self):
        print("Test de la position home")
        print("🔎 Recherche de ports disponibles...")
        ports = list_ports.comports()
        if not ports:
            print("❌ Aucun port série détecté.")
            exit(1)

        # Tu peux ajuster ici si tu sais exactement le port
        port = ports[0].device
        print(f"✅ Connexion au port {port}...")

        device = pydobot.Dobot(port=port, verbose=True)
        
        try:
            send_home_command(device)
        except Exception as e:
            print(f"⚠️ Erreur lors du test : {e}")
        finally:
            print("🔌 Déconnexion...")
            device.close()


if __name__ == "__main__":
    test = TestRobot()
    test_methods = [
        ("test_home", test.test_home),
        ("test_hauteur", test.test_hauteur),
        ("test_move_to_colonne", test.test_move_to_colonne),
        ("test_move_to", test.test_move_to),
        ("test_grab_pallet", test.test_grab_pallet),
    ]

    for test_name, test_method in test_methods:
        print(f"\n🔍 Exécution du test : {test_name}")
        try:
            test_method()
            print(f"✅ {test_name} réussi.")
        except Exception as e:
            print(f"❌ {test_name} échoué : {e}")

    print("\n🎉 Tous les tests sont terminés.")
