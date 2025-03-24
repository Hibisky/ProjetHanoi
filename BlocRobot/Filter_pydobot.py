import sys


class FilterPydobotLogs:
    """Filtre les logs contenant 'pydobot' pour éviter leur affichage."""

    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.buffer = ""  # Stocke temporairement la ligne en cours

    def write(self, message):
        self.buffer += message  # Ajoute le message au buffer

        if "\n" in message:  # Si le message contient une fin de ligne
            lines = self.buffer.split("\n")  # Sépare les lignes
            for line in lines[
                :-1
            ]:  # Traite toutes les lignes sauf la dernière incomplète
                if (
                    "pydobot" not in line
                ):  # Affiche uniquement si "pydobot" n'est pas dedans
                    self.original_stdout.write(line + "\n")
            self.buffer = lines[
                -1
            ]  # Conserve la dernière partie (potentiellement incomplète)

    def flush(self):
        if (
            self.buffer and "pydobot" not in self.buffer
        ):  # Affiche la dernière ligne si complète
            self.original_stdout.write(self.buffer)
        self.original_stdout.flush()
        self.buffer = ""  # Réinitialise le buffer
