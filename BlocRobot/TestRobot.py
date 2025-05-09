from BlocRobot.DobotControl import DobotControl
import time
from serial.tools import list_ports
import pydobot

class TestRobot:
    def __init__(self):
        print("Test de la position home")
        try:
            self.robot = DobotControl()
            time.sleep(30)
            print("✅ Robot initialisé avec succès.")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'initialisation du robot : {e}")
            self.robot = None

    def test_grab_pallet(self):
        """
        Test de la fonction grab_pallet du robot Dobot.
        """
        if not self.robot:
            print("⚠️ Robot non initialise. Test annule.")
            return
        print("Test de la fonction grab_pallet")
        try:
            self.robot.execute_init()
            self.robot.grab_pallet(1, grab=True)
            self.robot.grab_pallet(1, grab=False)
            self.robot.return_to_home()
            print("✅ Test grab_pallet réussi.")
        except Exception as e:
            print(f"❌ Erreur lors du test grab_pallet : {e}")

    def test_move_to(self):
        """
        Test de la fonction move_to du robot Dobot.
        """
        if not self.robot:
            print("⚠️ Robot non initialisé. Test annulé.")
            return
        print("Test de la fonction move_to")
        try:
            self.robot.execute_init()
            self.robot.move_to_and_check(200, 200, 150, 0, wait=True)
            self.robot.return_to_home()
            print("✅ Test move_to réussi.")
        except Exception as e:
            print(f"❌ Erreur lors du test move_to : {e}")

    def test_move_to_colonne(self):
        """
        Test de déplacement vers les colonnes.
        """
        if not self.robot:
            print("⚠️ Robot non initialisé. Test annulé.")
            return
        print("Test de déplacement vers les colonnes")
        try:
            self.robot.execute_init()
            self.robot.deplacer_vers_axe(1)
            self.robot.deplacer_vers_axe(2)
            self.robot.deplacer_vers_axe(3)
            self.robot.return_to_home()
            print("✅ Test move_to_colonne réussi.")
        except Exception as e:
            print(f"❌ Erreur lors du test move_to_colonne : {e}")

    def test_hauteur(self):
        """
        Test de la hauteur du robot.
        """
        if not self.robot:
            print("⚠️ Robot non initialisé. Test annulé.")
            return
        print("Test de la hauteur du robot")
        try:
            for hauteur in range(1, 6):
                print(f"🔄 Déplacement vers la colonne de droite hauteur {hauteur} pallets")
                self.robot.deplacer_vers_colonne_droite()
                self.robot.grab_pallet(hauteur, grab=True)
                self.robot.activate_ventouse(False)
            print("🔄 Déplacement vers la colonne de droite hauteur 0 pallets, dépose du palet")
            self.robot.deplacer_vers_colonne_droite()
            self.robot.grab_pallet(0, grab=False)
            print("✅ Test hauteur réussi.")
        except Exception as e:
            print(f"❌ Erreur lors du test hauteur : {e}")


if __name__ == "__main__":
    test = TestRobot()
    print("Démarrage des tests...")

    test_methods = [
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
    if test.robot:
        try:
            test.robot.disconnect()
            print("🔌 Déconnexion du robot.")
        except Exception as e:
            print(f"⚠️ Erreur lors de la déconnexion du robot : {e}")
        finally:
            if test.robot.device:
                test.robot.device.close()
                print("🔒 Connexion série fermée.")
