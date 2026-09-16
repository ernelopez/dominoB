# partida.py

from tablero import Tablero
from pozo import Pozo
from jugador import Jugador


class Partida:

    def __init__(self, archivo_fichas, fichas_por_jugador=6):

        # Tablero
        self.tablero = Tablero()

        # Pozo
        self.pozo = Pozo(archivo_fichas)

        # Jugadores
        self.jugadores = [
            Jugador("Jugador 1"),
            Jugador("Jugador 2")
        ]

        # Turno: índice de jugadores
        self.turno = 0

        # Estado de la partida
        self.terminada = False
        self.ganador = None

        # Flag: el jugador actual ya robó en este turno?
        self.ya_robo_en_turno = False
        self.ficha_robada = None

        # Reparto inicial
        self.fichas_por_jugador = fichas_por_jugador
        self.repartir_fichas()


    def repartir_fichas(self):
        """Reparte fichas a cada jugador"""
        for jugador in self.jugadores:
            for _ in range(self.fichas_por_jugador):
                ficha = self.pozo.sacar()
                if ficha is not None:
                    jugador.recibir_ficha(ficha)


    def jugador_actual(self):
        """Devuelve el jugador que tiene el turno"""
        return self.jugadores[self.turno]


    def cambiar_turno(self):
        """Cambia al siguiente jugador y resetea el flag de robo"""
        self.turno = (self.turno + 1) % len(self.jugadores)
        self.ya_robo_en_turno = False
        self.ficha_robada = None


    def puede_jugar(self, jugador):
        """Verifica si el jugador tiene alguna jugada posible con sus fichas actuales"""
        if jugador.cantidad_fichas() == 0:
            return False
        
        if self.tablero.primera_jugada:
            return True
        
        valor_head = self.tablero.head_posible.valor
        valor_tail = self.tablero.tail_posible.valor
        
        for ficha in jugador.fichas:
            for clave, valor in ficha.valores.items():
                if valor is not None:
                    if valor == valor_head or valor == valor_tail:
                        return True
        
        return False


    def puede_robar(self, jugador=None):
        """Verifica si el jugador puede robar del pozo"""
        if jugador is None:
            jugador = self.jugador_actual()
        
        if self.ya_robo_en_turno:
            return False
        
        if self.pozo.cantidad() == 0:
            return False
        
        return True


    def robar_ficha(self, jugador=None):
        """
        Roba una ficha del pozo.
        Retorna la ficha robada o None si no se puede.
        """
        if jugador is None:
            jugador = self.jugador_actual()
        
        if not self.puede_robar(jugador):
            return None
        
        ficha = self.pozo.sacar()
        if ficha is None:
            return None
        
        jugador.recibir_ficha(ficha)
        self.ya_robo_en_turno = True
        self.ficha_robada = ficha
        
        return ficha


    def pasar_turno(self, jugador=None):
        """
        Pasa el turno al siguiente jugador sin colocar ficha.
        Retorna True si se pudo pasar, False si no está permitido.
        """
        if jugador is None:
            jugador = self.jugador_actual()
        
        if not self.ya_robo_en_turno:
            return False
        
        self.cambiar_turno()
        return True


    def jugar_ficha(self, ficha, casilla):
        """
        Intenta colocar una ficha en una casilla.
        Solo cambia turno si tiene éxito.
        Retorna True si se colocó correctamente.
        """
        jugador = self.jugador_actual()
        
        if ficha not in jugador.fichas:
            return False
        
        if self.tablero.primera_jugada:
            colocada = self.tablero.colocar_primera_ficha(ficha, casilla)
        else:
            colocada = self.tablero.colocar_ficha(ficha, casilla)
        
        if not colocada:
            return False
        
        jugador.sacar_ficha(ficha)
        
        # --- VERIFICAR GANADOR ---
        if jugador.cantidad_fichas() == 0:
            self.terminada = True
            self.ganador = jugador
            return True
        
        # Si no ganó, cambiar turno
        self.cambiar_turno()
        return True


    def partida_bloqueada(self):
        """Verifica si la partida está bloqueada (nadie puede jugar ni robar)"""
        for jugador in self.jugadores:
            if self.puede_jugar(jugador) or self.puede_robar(jugador):
                return False
        return True


    def obtener_ganador_por_menos_fichas(self):
        """
        Cuando la partida se bloquea, gana el que tiene menos fichas.
        Si empatan en cantidad, gana el que tiene menos suma de valores.
        Retorna el jugador ganador o None si hay empate total.
        """
        j1 = self.jugadores[0]
        j2 = self.jugadores[1]
        
        if j1.cantidad_fichas() < j2.cantidad_fichas():
            return j1
        elif j2.cantidad_fichas() < j1.cantidad_fichas():
            return j2
        
        # Empate en cantidad: por suma de valores
        suma_j1 = 0
        for ficha in j1.fichas:
            for valor in ficha.valores.values():
                if valor is not None:
                    suma_j1 += valor
        
        suma_j2 = 0
        for ficha in j2.fichas:
            for valor in ficha.valores.values():
                if valor is not None:
                    suma_j2 += valor
        
        if suma_j1 < suma_j2:
            return j1
        elif suma_j2 < suma_j1:
            return j2
        else:
            return None


    def verificar_fin_partida(self):
        """
        Verifica si la partida debe terminar por bloqueo o pozo vacío.
        Retorna True si terminó, False si continúa.
        NOTA: La victoria por quedarse sin fichas ya se maneja en jugar_ficha()
        """
        if self.terminada:
            return True
        
        # NO verificar durante la primera jugada
        if self.tablero.primera_jugada:
            return False
        
        jugador = self.jugador_actual()
        
        # Caso 1: El jugador no puede jugar y el pozo está vacío (pierde)
        if self.pozo.cantidad() == 0 and not self.puede_jugar(jugador):
            self.terminada = True
            for j in self.jugadores:
                if j != jugador:
                    self.ganador = j
                    break
            return True
        
        # Caso 2: Ambos jugadores están bloqueados
        if self.partida_bloqueada():
            self.terminada = True
            self.ganador = self.obtener_ganador_por_menos_fichas()
            return True
        
        return False

    def determinar_ficha_inicial(self):
        """
        Encuentra la ficha inicial según las reglas del dominó:
        1. El doble mayor
        2. Si no hay dobles, la ficha con mayor suma
        Retorna (ficha, jugador)
        """
        mejor_ficha = None
        mejor_jugador = None
        mejor_valor = -1
        encontre_doble = False
        
        for jugador in self.jugadores:
            for ficha in jugador.fichas:
                # Verificar si es doble
                if ficha.valores["O"] == ficha.valores["E"]:
                    valor_doble = ficha.valores["O"]
                    # Si es el primer doble o es mayor que el mejor doble encontrado
                    if not encontre_doble or valor_doble > mejor_valor:
                        mejor_ficha = ficha
                        mejor_jugador = jugador
                        mejor_valor = valor_doble
                        encontre_doble = True
        
        # Si no se encontraron dobles, buscar la ficha con mayor suma
        if not encontre_doble:
            for jugador in self.jugadores:
                for ficha in jugador.fichas:
                    suma = ficha.valores["O"] + ficha.valores["E"]
                    if suma > mejor_valor:
                        mejor_ficha = ficha
                        mejor_jugador = jugador
                        mejor_valor = suma
        
        return mejor_ficha, mejor_jugador

    def colocar_ficha_inicial(self, ficha, casilla):
        """Coloca la ficha inicial sin cambiar el turno"""
        jugador = self.jugador_actual()
        
        if ficha not in jugador.fichas:
            return False
        
        colocada = self.tablero.colocar_primera_ficha(ficha, casilla)
        if not colocada:
            return False
        
        jugador.sacar_ficha(ficha)
        return True