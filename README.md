## Introduction

Dans le cadre d'un projet collectif de l'ecole Polytech tours, Nous avons concu pour les journées portes ouvertes et autres demonstrations un programme qui permet au robot DOTOT magician de jouer au JEU DE HANOI. Le robot analyse le set qui est placé devant lui et est capable de resoudre le jeu de Hanoi grace à ca caméra.


## Fonctionnalité 

- **Deplacement :** Le robot possede des deplacemenst pres defini qui lui permettent de jouer ( deplacer et poser aux bons endroit les palets) pendant toute sla durée du jeu
- **Algorithme :** Le robot est capable grace a un algorithme de definir son prochain coup basé sur la vision du jeu en temps réel
- **Caméra:** Une caméra est installé sur la tete du robot pour visualiser en temps réel le plateau de jeu.

## Prerequisites

Robot: 
    Installer le logiciel DOBOTSTUDIO DobotStudio (DOBOT Magician)
    https://www.dobot-robots.com/service/download-center

Plateau de jeu:
    Un plateau de jeu est necessaire avec les palets qui servirons de pions.
    Voir libraries impression 3D : ***************************

Caméra:
    Une caméra est necessaire pour que le robot connaisse l'emplacement des palets.
    Reference caméra pour le projet: WebCam 



## Libraries

Les libraries sont gére via l'environnement Poetry 
installation de poetry 
    sur mac 
    sur windows

## Dependencies

Caméra :
- opencv-python
- numpy 

Robot:
- pydobot
- pyserial

Interface:
- PyQt6

## Getting Started

Installer un environnement virtuel ou installer toutes les dependances logiciels en local.
Nous vous recommandons poetry 
 ```bash
    poetry init
    poetry add requirements.txt 
```
### Setup


2. **Run the Project:**
    ```bash
    poetry run python main.py
    ```
    ou 
    ```bash
    make run 
    ```

### Visualization


1. **Obtenir la dimension des palets:** 

2. **Run the visualization code:**
    ```bash
    make vision
    ```

## Architecture

```
PROJETHANOI/
├── __init__.py
├── BlocAlgo/
│   ├── __init__.py
│   └── HanoiIterative.py
├── BlocRobot/
│   ├── __init__.py
│   └── DobotControl.py
│   └── Filter_pydobot.py
│   └── requirements.py
├── BlocVision/
│   ├── __init__.py
│   └── DetectionInterface.py
│   └── SimulationMoves.py
│   └── requirements.py
├── BlocVision/
│   ├── __init__.py
│   └── CameraProcessor.py
│   └── requirements.py
├── Tests/
│   └── TestRobot.py
├── detections/
├── main.py
├── Makefile
├── README.md
```

## Structure diagram 

graph TD;
    
    subgraph Vision
        A[CameraProcessor] -->|Capture image| B[Détection disques]
        B -->|Envoie nombre disques| C[DetectionInterface]
    end
    
    subgraph Interface Utilisateur
        C -->|Validation utilisateur| D[Nombre de disques validé]
    end
    
    subgraph Algorithme
        D -->|Entrée| E[HanoiIterative]
        E -->|Génère séquence mouvements| F[SimulationMoves]
    end
    
    subgraph Simulation
        F -->|Affichage visuel| G[Utilisateur]
    end
    
    subgraph Robotique
        E -->|Liste mouvements| H[DobotControl]
        H -->|Exécute déplacements| I[Manipulation physique]
    end
    
    subgraph Programme Principal
        Start((Début)) -->|Init robot| H
        Start -->|Init caméra| A
        Start -->|Capture image| A
        A -->|Analyse tour| B
        B -->|Vérification utilisateur| C
        C -->|Confirme disques| D
        D -->|Lance algorithme| E
        E -->|Envoie mouvements| F
        F -->|Affichage simulation| G
        E -->|Envoie commandes| H
        H -->|Déplacement terminé| End((Fin))
    end



## Devices


- **Robot:** DOBOT Magician dotée d'une ventouse 

- **Python Visualization:** WebCam 

## Sequence Diagram: 


## Algoritm


## Future Enhancements
