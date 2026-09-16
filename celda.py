class Celda:

    def __init__(self, numero):

        self.numero = numero
        self.valor = None
        self.casilla = None

        # Centro de la celda en pantalla
        self.x = 0
        self.y = 0

    def mostrar(self):
        print(
            f"Celda {self.numero}: "
            f"x={self.x}, y={self.y}, "
            f"valor={self.valor}"
        )