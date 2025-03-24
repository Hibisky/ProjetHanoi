from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class DobotCalibrator(QWidget):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.y = robot.cible_y
        self.z = robot.cible_z
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.label = QLabel(f"X: {self.x}, Z: {self.z}")
        layout.addWidget(self.label)
        
        self.btn_y_up = QPushButton("Y +5")
        self.btn_y_up.clicked.connect(lambda: self.update_position(dy=5))
        layout.addWidget(self.btn_y_up)
        
        self.btn_y_down = QPushButton("Y -5")
        self.btn_y_down.clicked.connect(lambda: self.update_position(dy=-5))
        layout.addWidget(self.btn_y_down)
        
        self.btn_z_up = QPushButton("Z +5")
        self.btn_z_up.clicked.connect(lambda: self.update_position(dz=5))
        layout.addWidget(self.btn_z_up)
        
        self.btn_z_down = QPushButton("Z -5")
        self.btn_z_down.clicked.connect(lambda: self.update_position(dz=-5))
        layout.addWidget(self.btn_z_down)
        
        self.btn_save = QPushButton("Enregistrer")
        self.btn_save.clicked.connect(self.save_values)
        layout.addWidget(self.btn_save)
        
        self.setLayout(layout)
    
    def update_position(self, dy=0, dz=0):
        self.y += dy
        self.z += dz
        self.robot.move_to_and_check(self.y, self.z)
        self.label.setText(f"Y: {self.y}, Z: {self.z}")
    
    def save_values(self):
        self.robot.cible_y = self.y
        self.robot.cible_z = self.z
        print(f"✅ Calibration enregistrée: Y={self.robot.cible_y}, Z={self.robot.cible_z}")
        self.close()