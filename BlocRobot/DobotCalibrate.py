from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class DobotCalibrator(QWidget):
    def __init__(self, robot):
        """
        Classe de calibration du Dobot.
        :param robot: Instance de la classe DobotControl.
        """
        super().__init__()
        self.robot = robot
        pose = self.robot.get_pose()
        self.x = pose[0]  # Position actuelle du Dobot
        self.y = pose[1]
        self.z = pose[2]   
        self.dy = 0
        self.dz = 0     
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()

        # Affichage des coordonnées actuelles
        self.label = QLabel(f"X: {self.x}, Y: {self.y}, Z: {self.z}")
        layout.addWidget(self.label)

        # Fonction pour créer un groupe de boutons de contrôle pour un axe
        def create_axis_controls(axis_name, update_func, increments):
            axis_layout = QVBoxLayout()
            axis_label = QLabel(f"Contrôle {axis_name}")
            axis_layout.addWidget(axis_label)

            for increment in increments:
                btn = QPushButton(f"{axis_name} {'+' if increment > 0 else ''}{increment}")
                btn.clicked.connect(lambda _, inc=increment: update_func(inc))
                axis_layout.addWidget(btn)

            return axis_layout

        # Layout pour les boutons de contrôle X
        x_layout = create_axis_controls(
            "X",
            lambda dx: self.update_position(dx=dx),
            [5, -5, 10, -10]
        )
        layout.addLayout(x_layout)

        # Layout pour les boutons de contrôle Y
        y_layout = create_axis_controls(
            "Y",
            lambda dy: self.update_position(dy=dy),
            [5, -5, 10, -10]
        )
        layout.addLayout(y_layout)

        # Layout pour les boutons de contrôle Z
        z_layout = create_axis_controls(
            "Z",
            lambda dz: self.update_position(dz=dz),
            [5, -5, 10, -10]
        )
        layout.addLayout(z_layout)

        # Bouton pour enregistrer les valeurs
        self.btn_save = QPushButton("Enregistrer")
        self.btn_save.clicked.connect(self.save_values)
        layout.addWidget(self.btn_save)

        # Appliquer le layout principal
        self.setLayout(layout)
    
    def update_position(self, dy=0, dz=0, dx=0):
        """"
        Met à jour la position du Dobot en fonction des valeurs fournies."
        :param dy: Valeur à ajouter à la coordonnée Y."
        :param dz: Valeur à ajouter à la coordonnée Z."
        :param dx: Valeur à ajouter à la coordonnée X."
        """
        self.dy += dy
        self.dz += dz
        self.x += dx
        self.y += dy
        self.z += dz
        self.robot.move_to_and_check(self.x, self.y, self.z)
        self.label.setText(f"X: {self.x} Y: {self.y}, Z: {self.z}")
    
    def save_values(self):
        """
        Enregistre les valeurs de calibration dans l'objet robot.
        """
        self.robot.CALIB_X = self.robot.x + self.dx
        self.robot.CALIB_Y = self.robot.y + self.dy
        self.robot.CALIB_Z = self.robot.z + self.dz
        print(f"✅ Calibration enregistrée: Y={self.robot.CALIB_Y}, Z={self.robot.CALIB_Z}")
        self.close()