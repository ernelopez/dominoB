from celda import Celda
from config import CANT_CASILLAS, CANT_CASILLAS_TOP

class Casilla:

    def __init__(self,
                 numero,
                 orientacion,
                 sentido,
                 celda1,
                 celda2,
                 x,
                 y):

        self.numero = numero
        self.orientacion = orientacion
        # +1: el recorrido coincide con la geometría
        # -1: el recorrido es inverso a la geometría
        self.sentido = sentido

        # Esquina superior izquierda de la casilla
        self.x = x
        self.y = y

        #celda1 será O ó N; celda2 será E ó S
        if sentido==1 :
            self.celda1 = Celda(celda1)
            self.celda2 = Celda(celda2)
        else :
            self.celda1 = Celda(celda2)
            self.celda2 = Celda(celda1)

        self.celda1.casilla = self
        self.celda2.casilla = self

        self.ficha = None

    def calcular_posiciones_celdas(self,
                                   largo_ficha,
                                   ancho_ficha):

        if self.orientacion == "horizontal":
            if self.sentido==1 :
                self.celda1.x = self.x + ancho_ficha / 2
                self.celda1.y = self.y + ancho_ficha / 2

                self.celda2.x = self.x + largo_ficha - ancho_ficha / 2
                self.celda2.y = self.y + ancho_ficha / 2
            else :
                self.celda2.x = self.x + ancho_ficha / 2
                self.celda2.y = self.y + ancho_ficha / 2

                self.celda1.x = self.x + largo_ficha - ancho_ficha / 2
                self.celda1.y = self.y + ancho_ficha / 2

        else:
            if self.sentido==1 :
                self.celda1.x = self.x + ancho_ficha / 2
                self.celda1.y = self.y + ancho_ficha / 2

                self.celda2.x = self.x + ancho_ficha / 2
                self.celda2.y = self.y + largo_ficha - ancho_ficha / 2
            else :
                self.celda2.x = self.x + ancho_ficha / 2
                self.celda2.y = self.y + ancho_ficha / 2

                self.celda1.x = self.x + ancho_ficha / 2
                self.celda1.y = self.y + largo_ficha - ancho_ficha / 2

        #Parche para trocar los centros de las de abajo y a la izquierda
        if self.sentido == -1:
            self.celda1.x, self.celda2.x = self.celda2.x, self.celda1.x
            self.celda1.y, self.celda2.y = self.celda2.y, self.celda1.y


    def casilla_siguiente_head(self, tablero):

        return tablero.casillas[(self.numero + 1) % CANT_CASILLAS]


    def casilla_siguiente_tail(self, tablero):

        return tablero.casillas[(self.numero - 1) % CANT_CASILLAS]