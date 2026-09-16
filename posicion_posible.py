from config import CANT_CASILLAS, CANT_CASILLAS_TOP

CANT_CELDAS = 2*CANT_CASILLAS
CANT_CASILLAS_LAT = CANT_CASILLAS//2-CANT_CASILLAS_TOP

CASILLAS_TOP = list(range(CANT_CASILLAS_TOP))
CASILLAS_RIG = list(range(CANT_CASILLAS_TOP,CANT_CASILLAS_TOP+CANT_CASILLAS_LAT))
CASILLAS_DOW = [i+CANT_CASILLAS//2 for i in CASILLAS_TOP]
CASILLAS_LEF = [i+CANT_CASILLAS//2 for i in CASILLAS_RIG]

CELDAS_TOP = [x*2 + i for x in CASILLAS_TOP for i in (0, 1)]
CELDAS_RIG = [x*2 + i for x in CASILLAS_RIG for i in (0, 1)]
CELDAS_DOW = [x*2 + i for x in CASILLAS_DOW for i in (0, 1)]
CELDAS_LEF = [x*2 + i for x in CASILLAS_LEF for i in (0, 1)]

class PosicionPosible:

    def __init__(self):

        # Casilla donde se puede colocar la ficha
        self.casilla = None

        # Celda concreta de la casilla donde debe
        # caer el extremo que hace match
        self.celda = None

        # Valor que debe coincidir
        self.valor = None

        # Orientación que debe tener la ficha
        self.orientacion = None

        # Posición de la ficha que debe matchear
        # esa celda: "O", "E", "N" o "S"
        self.posicion = None


    def inicializar(self, casilla, celda, valor):

        direccion = casilla.orientacion
        self.casilla = casilla
        self.celda = celda
        #self.direccion = direccion
        self.valor = valor
        self.orientacion = direccion
        
        if direccion == "horizontal" and celda.numero in CELDAS_TOP and celda.numero%2==0 :
            self.posicion = "O"
        elif direccion == "horizontal" and celda.numero in CELDAS_TOP and celda.numero%2==1 :
            self.posicion = "E"
        elif direccion == "vertical" and celda.numero in CELDAS_RIG and celda.numero%2==0 :
            self.posicion = "N"
        elif direccion == "vertical" and celda.numero in CELDAS_RIG and celda.numero%2==1 :
            self.posicion = "S"
        elif direccion == "horizontal" and celda.numero in CELDAS_DOW and celda.numero%2==0 :
            self.posicion = "E"
        elif direccion == "horizontal" and celda.numero in CELDAS_DOW and celda.numero%2==1 :
            self.posicion = "O"
        elif direccion == "vertical" and celda.numero in CELDAS_LEF and celda.numero%2==0 :
            self.posicion = "S"
        elif direccion == "vertical" and celda.numero in CELDAS_LEF and celda.numero%2==1 :
            self.posicion = "N"


    def mostrar(self):
        print(f"Casilla     : {self.casilla.numero}")
        print(f"Celda       : {self.celda.numero}")
        print(f"Debe haber  : {self.valor}")
        print(f"Orientación : {self.orientacion}")
        print(f"Posición    : {self.posicion}")

    def texto(self):
        """Devuelve el valor como fracción legible"""
        return f"{self.valor}"  # O usa el formato que prefieras