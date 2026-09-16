import csv
import random
from ficha import Ficha


class Pozo:

    def __init__(self, archivo):
        self.fichas = []
        self.cargar(archivo)


    def cargar(self, archivo):
        with open(archivo, newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)

            for fila in lector:
                ficha = Ficha(
                    (
                        fila["izq_num"].strip(),
                        fila["izq_den"].strip()
                    ),
                    (
                        fila["der_num"].strip(),
                        fila["der_den"].strip()
                    )
                )
                self.fichas.append(ficha)

        random.shuffle(self.fichas)


    def sacar(self):
        if not self.fichas:
            return None
        return self.fichas.pop()


    def cantidad(self):
        return len(self.fichas)