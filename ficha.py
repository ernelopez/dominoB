from fractions import Fraction
from decimal import Decimal


class Ficha:

    def __init__(self, valor1, valor2):
        """
        valor1 y valor2 son tuplas (num, den) donde num y den son strings.
        Ejemplo: ("50", "100"), ("0.50", "1")
        """

        # -------------------------------------------------
        # Valores matemáticos (guardados como Fraction)
        # -------------------------------------------------
        self.valores = {}
        self.valores["O"] = self._a_fraction(valor1[0], valor1[1])
        self.valores["E"] = self._a_fraction(valor2[0], valor2[1])
        self.valores["N"] = None
        self.valores["S"] = None

        # -------------------------------------------------
        # Textos para mostrar (formato argentino)
        # -------------------------------------------------
        self.textos = {}
        self.textos["O"] = self._formatear_texto(valor1[0], valor1[1])
        self.textos["E"] = self._formatear_texto(valor2[0], valor2[1])
        self.textos["N"] = None
        self.textos["S"] = None

        # -------------------------------------------------
        # Orientación visual
        # -------------------------------------------------
        self.orientacion = "horizontal"

        # -------------------------------------------------
        # Casilla que ocupa en el tablero
        # -------------------------------------------------
        self.casilla = None

        # -------------------------------------------------
        # Estado de la ficha
        # "pozo", "mano", "tablero"
        # -------------------------------------------------
        self.estado = "pozo"

        # -------------------------------------------------
        # Jugador dueño
        # None si está en el tablero
        # -------------------------------------------------
        self.duenio = None


    def _a_fraction(self, num_str, den_str):
        """Convierte (num, den) en Fraction de forma exacta."""
        num = Fraction(Decimal(num_str))
        den = Fraction(Decimal(den_str))
        return num / den


    def _formatear_numero(self, num_str):
        """
        Formatea un número string aplicando formato argentino:
        - Coma decimal
        - Punto como separador de miles
        - Mantiene los ceros originales
        """
        # Reemplazar punto decimal por coma
        if "." in num_str:
            entero, decimales = num_str.split(".")
        else:
            entero = num_str
            decimales = None

        # Aplicar separador de miles (punto cada 3 dígitos desde la derecha)
        if len(entero) > 3:
            entero_formateado = ""
            for i, digito in enumerate(reversed(entero)):
                if i > 0 and i % 3 == 0:
                    entero_formateado = "." + entero_formateado
                entero_formateado = digito + entero_formateado
        else:
            entero_formateado = entero

        # Unir con coma decimal si hay decimales
        if decimales is not None:
            return entero_formateado + "," + decimales
        else:
            return entero_formateado


    def _formatear_texto(self, num_str, den_str):
        """
        Devuelve el texto que se mostrará para un lado.
        - Si den == 1: solo el número (ej: '0,50')
        - Si den != 1: fracción con salto (ej: '50\n100')
        """
        num_fmt = self._formatear_numero(num_str)

        # Si el denominador es 1, solo mostrar el numerador
        if Decimal(den_str) == Decimal("1"):
            return num_fmt

        den_fmt = self._formatear_numero(den_str)
        return f"{num_fmt}\n{den_fmt}"


    def girar_90(self):
        """
        Gira la ficha 90 grados en sentido antihorario.
        """
        # Guardamos los cuatro valores actuales
        O = self.valores["O"]
        E = self.valores["E"]
        N = self.valores["N"]
        S = self.valores["S"]

        # Guardamos los cuatro textos actuales
        texto_O = self.textos["O"]
        texto_E = self.textos["E"]
        texto_N = self.textos["N"]
        texto_S = self.textos["S"]

        # -------------------------------------------------
        # Rotación antihoraria:
        # E → N
        # S → E
        # O → S
        # N → O
        # -------------------------------------------------
        self.valores["N"] = E
        self.valores["O"] = N
        self.valores["S"] = O
        self.valores["E"] = S

        self.textos["N"] = texto_E
        self.textos["O"] = texto_N
        self.textos["S"] = texto_O
        self.textos["E"] = texto_S

        # Cambia la orientación
        if self.orientacion == "horizontal":
            self.orientacion = "vertical"
        else:
            self.orientacion = "horizontal"


    def mostrar_ficha(self):
        print(
            self.orientacion,
            f"O:{self.textos['O']}",
            f"E:{self.textos['E']}",
            f"N:{self.textos['N']}",
            f"S:{self.textos['S']}"
        )


    def mostrar_valores(self):
        """Devuelve una representación legible de la ficha."""
        if self.orientacion == "horizontal":
            return f"[{self.textos['O']} | {self.textos['E']}]".replace("\n", "/")
        else:
            return f"[{self.textos['N']} | {self.textos['S']}]".replace("\n", "/")


    def __str__(self):
        return self.mostrar_valores()

    def __repr__(self):
        return self.mostrar_valores()