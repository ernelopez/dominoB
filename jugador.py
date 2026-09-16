class Jugador:

    def __init__(self, nombre):

        self.nombre = nombre
        self.fichas = []


    def recibir_ficha(self, ficha):

        self.fichas.append(ficha)

        ficha.estado = "mano"
        ficha.duenio = self


    def sacar_ficha(self, ficha):

        if ficha not in self.fichas:
            return False

        self.fichas.remove(ficha)

        ficha.duenio = None

        return True


    def cantidad_fichas(self):

        return len(self.fichas)


    def mostrar_fichas(self):

        print(f"\n=== FICHAS DE {self.nombre.upper()} ===")

        for i, ficha in enumerate(self.fichas):

            print(f"{i}: ", end="")
            ficha.mostrar_ficha()