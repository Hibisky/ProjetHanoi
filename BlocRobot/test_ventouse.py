#Magician
#import DobotDllType as dType
import time
import math

print("Connexion r�ussie au Dobot!")

# Exemple de position pour tester la ventouse
x = 250  # Position en X
y = 0    # Position en Y
z = 50   # Hauteur au-dessus de l'objet
r = 0    # Orientation du bras

# D�placement vers la position cible
dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x, y, z, r, isQueued = 1)
time.sleep(2)  # Attendre que le bras se d�place

# Activer la ventouse
dType.SetEndEffectorSuctionCup(api, enableCtrl=1, on=1, isQueued=1)
print("Ventouse activ�e")
time.sleep(3)  # Attendre 3 secondes

# D�sactiver la ventouse
dType.SetEndEffectorSuctionCup(api, enableCtrl=1, on=0, isQueued=1)
print("Ventouse d�sactiv�e")