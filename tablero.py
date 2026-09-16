from casilla import Casilla
from config import LARGO_FICHA, ANCHO_FICHA, MARGEN_TABLERO, CANT_CASILLAS, CANT_CASILLAS_TOP
from posicion_posible import PosicionPosible

CANT_CELDAS = 2*CANT_CASILLAS
CANT_CASILLAS_LAT = CANT_CASILLAS//2-CANT_CASILLAS_TOP

class Tablero:

    def __init__(self):

        self.casillas = []
        self.celdas = [None] * CANT_CELDAS

        self.head_posible = PosicionPosible()
        self.tail_posible = PosicionPosible()

        self.crear_casillas()

        self.primera_jugada = True
        self.fichas_jugadas = []


    def agregar_casilla(self, casilla):

        casilla.calcular_posiciones_celdas(
            LARGO_FICHA,
            ANCHO_FICHA
        )

        self.casillas.append(casilla)

        self.celdas[casilla.celda1.numero] = casilla.celda1
        self.celdas[casilla.celda2.numero] = casilla.celda2


    def crear_casillas(self):

        numero = 0

        # -------------------------
        # Superior
        # -------------------------

        x = MARGEN_TABLERO + ANCHO_FICHA
        y = MARGEN_TABLERO

        for _ in range(CANT_CASILLAS_TOP):

            casilla = Casilla(
                numero,
                "horizontal",1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            x += LARGO_FICHA


        # -------------------------
        # Derecha
        # -------------------------

        x = MARGEN_TABLERO + ANCHO_FICHA + CANT_CASILLAS_TOP * LARGO_FICHA
        y = MARGEN_TABLERO

        for _ in range(CANT_CASILLAS_LAT):

            casilla = Casilla(
                numero,
                "vertical",1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            y += LARGO_FICHA


        # -------------------------
        # Inferior
        # -------------------------

        x = MARGEN_TABLERO + ANCHO_FICHA + CANT_CASILLAS_TOP * LARGO_FICHA  - LARGO_FICHA
        y = MARGEN_TABLERO + CANT_CASILLAS_LAT * LARGO_FICHA - ANCHO_FICHA

        for _ in range(CANT_CASILLAS_TOP):

            casilla = Casilla(
                numero,
                "horizontal",-1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            x -= LARGO_FICHA


        # -------------------------
        # Izquierda
        # -------------------------

        x = MARGEN_TABLERO
        y = MARGEN_TABLERO + (CANT_CASILLAS_LAT-1) * LARGO_FICHA

        for _ in range(CANT_CASILLAS_LAT):

            casilla = Casilla(
                numero,
                "vertical",-1,
                2 * numero,
                2 * numero + 1,
                x,
                y
            )

            self.agregar_casilla(casilla)

            numero += 1
            y -= LARGO_FICHA



    def colocar_primera_ficha(self, ficha, casilla):

        # La orientación de la ficha debe coincidir
        # con la orientación de la casilla.
        if ficha.orientacion != casilla.orientacion:
            print("MAL")
            return False

        # -------------------------------------------------
        # Colocar la ficha
        # -------------------------------------------------

        casilla.ficha = ficha
        ficha.casilla = casilla
        ficha.estado = "tablero"


        # -------------------------------------------------
        # Guardar los valores de la ficha en las celdas
        # -------------------------------------------------

        if casilla.orientacion == "horizontal":

            casilla.celda1.valor = ficha.valores["O"]
            casilla.celda2.valor = ficha.valores["E"]

        else:

            casilla.celda1.valor = ficha.valores["N"]
            casilla.celda2.valor = ficha.valores["S"]


        # -------------------------------------------------
        # Crear posición posible para TAIL
        # -------------------------------------------------

        casilla_tail = self.casillas[
            (casilla.numero - 1) % CANT_CASILLAS ]
        celda_tail = self.celdas[casilla_tail.numero*2+1]
        if casilla.numero < CANT_CASILLAS_TOP :
            valor_tail = ficha.valores["O"]
        elif casilla.numero < CANT_CASILLAS_TOP+CANT_CASILLAS_LAT :
            valor_tail = ficha.valores["N"]
        elif casilla.numero < CANT_CASILLAS_TOP+CANT_CASILLAS_LAT+CANT_CASILLAS_TOP :
            valor_tail = ficha.valores["E"]
        else :
            valor_tail = ficha.valores["S"]

        self.tail_posible.inicializar(casilla_tail,
                                      celda_tail,
                                      #casilla_tail.orientacion,
                                      valor_tail)

        # -------------------------------------------------
        # Crear posición posible para HEAD
        # -------------------------------------------------

        casilla_head = self.casillas[
            (casilla.numero + 1) % CANT_CASILLAS ]

        celda_head = self.celdas[casilla_head.numero*2]
        if casilla.numero < CANT_CASILLAS_TOP :
            valor_head = ficha.valores["E"]
        elif casilla.numero < CANT_CASILLAS_TOP+CANT_CASILLAS_LAT :
            valor_head = ficha.valores["S"]
        elif casilla.numero < CANT_CASILLAS_TOP+CANT_CASILLAS_LAT+CANT_CASILLAS_TOP :
            valor_head = ficha.valores["O"]
        else :
            valor_head = ficha.valores["N"]

        self.head_posible.inicializar(casilla_head,
                                      celda_head,
                                     # casilla_head.orientacion,
                                      valor_head)
        
        #Guardar la jugada en fichas_jugadas
        self.fichas_jugadas.append((ficha, casilla))
        self.primera_jugada = False

        return True


    def mostrar_casillas(self):

        print("\n=== CASILLAS ===\n")

        for casilla in self.casillas:

            print(
                f"{casilla.numero:2d}  "
                f"{casilla.orientacion:10s}  "
                f"({casilla.x:3d},{casilla.y:3d})  "
                f"celdas=({casilla.celda1.numero:2d},{casilla.celda2.numero:2d})"
            )


    def mostrar_celdas(self):

        print("\n=== CELDAS ===\n")

        for celda in self.celdas:

            print(
                f"{celda.numero:2d}  "
                f"({celda.x:6.1f},{celda.y:6.1f})  "
                f"casilla={celda.casilla.numero:2d}"
            )


    def puede_colocar(self, ficha, casilla):

        # -------------------------------------------------
        # Chequeo si coincide con head_posible
        # -------------------------------------------------

        if (
            casilla.numero == self.head_posible.casilla.numero
            and
            ficha.orientacion == self.head_posible.orientacion
        ):

            hv = self.head_posible.valor
            hp = self.head_posible.posicion

            fv = ficha.valores[hp]

            if hv == fv:

                #print("Eureka head")
                return self.head_posible, "head"


        # -------------------------------------------------
        # Chequeo si coincide con tail_posible
        # -------------------------------------------------

        if (
            casilla.numero == self.tail_posible.casilla.numero
            and
            ficha.orientacion == self.tail_posible.orientacion
        ):

            tv = self.tail_posible.valor
            tp = self.tail_posible.posicion

            fv = ficha.valores[tp]

            if tv == fv:

                #print("Eureka tail")
                return self.tail_posible, "tail"


        # -------------------------------------------------
        # No se puede colocar
        # -------------------------------------------------

        return None, None



    def colocar_ficha(self, ficha, casilla):

        posible , extremo = self.puede_colocar(ficha, casilla)
        # -------------------------------------------------
        # 1. Verificar que la jugada sea válida
        # -------------------------------------------------

        if not posible:
            return False
        else :
            if posible.posicion == "N" :
                nuevo_valor = ficha.valores["S"]
            elif posible.posicion == "S" :
                nuevo_valor = ficha.valores["N"]
            elif posible.posicion == "E" :
                nuevo_valor = ficha.valores["O"]
            else :
                nuevo_valor = ficha.valores["E"]

        # -------------------------------------------------
        # 3. Colocar la ficha
        # -------------------------------------------------

        casilla.ficha = ficha
        ficha.casilla = casilla
        ficha.estado = "tablero"


        # -------------------------------------------------
        # 4. Copiar los valores de la ficha a las celdas
        # -------------------------------------------------

        if casilla.orientacion == "horizontal":

            casilla.celda1.valor = ficha.valores["O"]
            casilla.celda2.valor = ficha.valores["E"]

        else:

            casilla.celda1.valor = ficha.valores["N"]
            casilla.celda2.valor = ficha.valores["S"]


        # -------------------------------------------------
        # 5. Actualizar la posición posible correspondiente
        # -------------------------------------------------

        if extremo == "tail":

            nueva_casilla = self.casillas[
                (casilla.numero - 1) % CANT_CASILLAS
            ]

            nueva_celda = self.celdas[
                nueva_casilla.numero * 2 + 1
            ]

            self.tail_posible.inicializar(
                nueva_casilla,
                nueva_celda,
                nuevo_valor
            )

        else:

            nueva_casilla = self.casillas[
                (casilla.numero + 1) % CANT_CASILLAS
            ]

            nueva_celda = self.celdas[
                nueva_casilla.numero * 2
            ]

            self.head_posible.inicializar(
                nueva_casilla,
                nueva_celda,
                nuevo_valor
            )

        self.fichas_jugadas.append((ficha, casilla))

        return True



    def fichas_jugadas(self):

        jugadas = []

        for casilla in self.casillas:

            if casilla.ficha is not None:

                jugadas.append(
                    (
                        casilla.numero,
                        casilla.ficha,
                        casilla.celda1.numero,
                        casilla.celda2.numero
                    )
                )

        return jugadas