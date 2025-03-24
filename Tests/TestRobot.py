from BlocRobot.DobotControl import DobotControl


class TestRobot:

    def testGrabPallet(self):
        robot = DobotControl()
        robot.execute_init()
        robot.grab_pallet(1, grab=True)
        robot.grab_pallet(1, grab=False)
        robot.return_to_home()
        robot.disconnect()

    def testMoveTo(self):
        robot = DobotControl()
        robot.execute_init()
        robot.move_to(200, 200, 150, 0, wait=True)
        robot.return_to_home()
        robot.disconnect()

    def testMoveToColonne(self):
        robot = DobotControl()
        robot.execute_init()
        robot.deplacer_vers_axe(1)
        robot.deplacer_vers_axe(2)
        robot.deplacer_vers_axe(3)
        robot.return_to_home()
        robot.disconnect()

    def testHauteur():
        print(f"Test de la hauteur")


if __name__ == "__main__":
    test = TestRobot()
    test.testGrabPallet()
    test.testMoveTo()
    test.testMoveToColonne()

    print("Tests terminés.")
