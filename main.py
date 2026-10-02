# pygame_app.py

import pygame
import sys
import os
from partida import Partida
from config import LARGO_FICHA, ANCHO_FICHA, MARGEN_TABLERO
import asyncio

# Constantes de pantalla (se recalcularán dinámicamente)
COLOR_FONDO = (40, 40, 40)
COLOR_BOTON = (70, 70, 70)
COLOR_BOTON_HOVER = (100, 100, 100)
COLOR_TEXTO_BOTON = (255, 255, 255)
COLOR_CASILLA_VACIA = (255, 255, 200)  # Rosa claro (255, 182, 193)
COLOR_CASILLA_DESTACADA = (50, 200, 50)

# Colores de jugadores
COLOR_JUGADOR1 = (200, 100, 100)  # Rojo suave
COLOR_JUGADOR2 = (100, 150, 220)  # Azul suave
COLOR_TEXTO = (255, 255, 255)
COLOR_TITULO = (255, 255, 200)

ANCHO_PANTALLA = 1200
ALTO_PANTALLA = 750

archivofuente = 'junegull.ttf'


class Boton:
    def __init__(self, x, y, ancho, alto, texto, imagen=None, color=COLOR_BOTON, color_hover=COLOR_BOTON_HOVER):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.imagen = imagen
        self.color = color
        self.color_hover = color_hover
        self.activo = True
        self.fuente = None
    
    def dibujar(self, pantalla, fuente):
        if self.imagen is not None:
            img = pygame.transform.smoothscale(self.imagen, (self.rect.width, self.rect.height))
            pantalla.blit(img, (self.rect.x, self.rect.y))
        else:
            color = self.color_hover if self.esta_sobre() and self.activo else self.color
            pygame.draw.rect(pantalla, color, self.rect, border_radius=8)
            pygame.draw.rect(pantalla, (150, 150, 150), self.rect, 2, border_radius=8)
        
        if self.texto:
            if self.activo:
                texto_surface = fuente.render(self.texto, True, COLOR_TEXTO_BOTON)
            else:
                texto_surface = fuente.render(self.texto, True, (180, 180, 180))
                texto_surface.set_alpha(128)
            
            texto_rect = texto_surface.get_rect(center=self.rect.center)
            
            if "Reiniciar" in self.texto or "Ayuda" in self.texto:
                texto_rect.y -= 5
                texto_rect.x -= 5
            
            pantalla.blit(texto_surface, texto_rect)
    
    def esta_sobre(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def click(self):
        return self.activo and self.esta_sobre()


class JuegoPygame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("sonidos/loop.mp3")
        pygame.mixer.music.play(-1)
        
        # Nombres de jugadores
        self.nombre_jugador1 = "Jugador 1"
        self.nombre_jugador2 = "Jugador 2"
        self.nombres_ingresados = False
        self.ingresando_nombre = 0
        self.mostrar_input_nombres = False
        
        if hasattr(sys, 'pygodide'):
            self.ancho_pantalla = ANCHO_PANTALLA
            self.alto_pantalla = ALTO_PANTALLA
            self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        else:
            info = pygame.display.Info()
            self.ancho_pantalla = info.current_w
            self.alto_pantalla = info.current_h
            self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla), pygame.FULLSCREEN)

        pygame.display.set_caption("Dominó de expresiones decimales")
        self.clock = pygame.time.Clock()
        
        self.recalcular_tamanos()
        self.cargar_imagenes()
        
        # Crear partida y determinar ficha inicial
        self.partida = Partida("fichas2.csv", fichas_por_jugador=6)
        self.ficha_inicial, self.jugador_inicial = self.partida.determinar_ficha_inicial()

        # Forzar el turno al jugador que comienza
        self.partida.turno = self.partida.jugadores.index(self.jugador_inicial)

        # Calcular offset para centrar el tablero
        self.calcular_offset_tablero()
        
        # Estado del juego
        self.ficha_seleccionada = None
        self.ficha_arrastrada = None
        self.ficha_robada_actual = None
        self.ficha_clickeada = None
        self.pos_click_x = 0
        self.pos_click_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.casillas_destacadas = []
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.mensaje_color = (255, 255, 255)

        self.mostrar_confirmacion_reinicio = False
        self.mensaje_confirmacion = ""
        self.mostrar_ayuda = False

        self.posiciones_fichas = {
            "jugador1": [],
            "jugador2": []
        }
        self.actualizar_posiciones_fichas()

        # Flag para saber si la ficha inicial ya fue colocada
        self.ficha_inicial_colocada = False
        
        self.crear_botones()
        self.actualizar_botones()

        self.volver_a_input = False
        self.mostrar_confirmacion_salir = False

        self.cambio_regla_error = True  # True: pasa turno si no encaja | False: comportamiento viejo

        self.mostrar_lupa = False
        self.tiempo_lupa = 0

        
    def dibujar_input_nombres(self):
        self.pantalla.fill(COLOR_FONDO)
        
        centro_x = self.ancho_pantalla // 2
        centro_y = self.alto_pantalla // 2
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_fuente = os.path.join(script_dir, "fonts", archivofuente)
        fuente_input = pygame.font.Font(ruta_fuente, int(32 * self.escala))
        
        # Título
        titulo_juego = self.fuente_grande.render("Dominó de expresiones decimales", True, COLOR_TITULO)
        self.pantalla.blit(titulo_juego, (centro_x - titulo_juego.get_width() // 2, centro_y - 450))
        
        # Subtítulo
        subtitulo = fuente_input.render("Ingresá los nombres de los jugadores", True, (255, 255, 255))
        self.pantalla.blit(subtitulo, (centro_x - subtitulo.get_width() // 2, centro_y - 300))
        
        # Jugador 1
        texto_j1 = fuente_input.render("Jugador 1:", True, COLOR_JUGADOR1)
        self.pantalla.blit(texto_j1, (centro_x - 350, centro_y - 180))
        
        rect_j1 = pygame.Rect(centro_x - 80, centro_y - 210, 350, 80)
        if self.ingresando_nombre == 1:
            pygame.draw.rect(self.pantalla, (200, 200, 200), rect_j1, 3)
        else:
            pygame.draw.rect(self.pantalla, (80, 80, 80), rect_j1, 2)
        texto = fuente_input.render(self.nombre_jugador1, True, COLOR_JUGADOR1)
        self.pantalla.blit(texto, (rect_j1.x + 15, rect_j1.y + 25))

        
        # Jugador 2
        texto_j2 = fuente_input.render("Jugador 2:", True, COLOR_JUGADOR2)
        self.pantalla.blit(texto_j2, (centro_x - 350, centro_y - 90))
        
        
        rect_j2 = pygame.Rect(centro_x - 80, centro_y - 115, 350, 80)
        if self.ingresando_nombre == 2:
            pygame.draw.rect(self.pantalla, (200, 200, 200), rect_j2, 3)
        else:
            pygame.draw.rect(self.pantalla, (80, 80, 80), rect_j2, 2)
        texto = fuente_input.render(self.nombre_jugador2, True, COLOR_JUGADOR2)
        self.pantalla.blit(texto, (rect_j2.x + 15, rect_j2.y + 25))
        
        # Instrucciones
        instrucciones = fuente_input.render("Hacé clic en una caja para editarla. Presioná ENTER para comenzar.", True, (200, 200, 200))
        self.pantalla.blit(instrucciones, (centro_x - instrucciones.get_width() // 2, centro_y + 30))  

        # ============================================
        # LOGOS
        # ============================================
        escala_baa = 0.5 * self.escala   # Ajustá este valor

        ancho_baa = int(self.img_baa.get_width() * escala_baa)
        alto_baa = int(self.img_baa.get_height() * escala_baa)

        img_baa = pygame.transform.smoothscale(self.img_baa, (ancho_baa, alto_baa))
        
        separacion = int(10 * self.escala)
        centro_x = self.ancho_pantalla // 2

        # Posición vertical
        #y_imagenes = self.alto_pantalla - int(220 * self.escala)
        y_imagenes = self.alto_pantalla - int(400 * self.escala)

        self.pantalla.blit(img_baa, (centro_x - ancho_baa // 2, y_imagenes + alto_baa + separacion))        
    
    def recalcular_tamanos(self):
        BASE_ANCHO = ANCHO_PANTALLA
        BASE_ALTO = ALTO_PANTALLA
        self.escala_x = self.ancho_pantalla / BASE_ANCHO
        self.escala_y = self.alto_pantalla / BASE_ALTO
        self.escala = min(self.escala_x, self.escala_y)

        self.largo_ficha = int(LARGO_FICHA * self.escala)
        self.ancho_ficha = int(ANCHO_FICHA * self.escala)
        self.margen_tablero = int(MARGEN_TABLERO * self.escala)
        
        self.tamano_fuente = max(12, int(24 * self.escala))
        self.tamano_fuente_grande = max(16, int(48 * self.escala))
        self.tamano_fuente_fraccion = max(10, int(20 * self.escala))
        
        print(f"📐 Escalado: {self.escala:.2f}x")
        print(f"   Ficha: {self.largo_ficha}x{self.ancho_ficha}")
        print(f"   Fuente: {self.tamano_fuente}px")

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            ruta_fuente = os.path.join(script_dir, "fonts", archivofuente)
            self.ruta_fuente = ruta_fuente
            self.fuente = pygame.font.Font(ruta_fuente, self.tamano_fuente)
            self.fuente_grande = pygame.font.Font(ruta_fuente, self.tamano_fuente_grande)
            self.fuente_fraccion = pygame.font.Font(ruta_fuente, self.tamano_fuente_fraccion)
            print("✅ Tipografía cargada correctamente")
        except Exception as e:
            print(f"⚠️ Error cargando tipografía: {e}")
            self.fuente = pygame.font.Font(None, self.tamano_fuente)
            self.fuente_grande = pygame.font.Font(None, self.tamano_fuente_grande)
            self.fuente_fraccion = pygame.font.Font(None, self.tamano_fuente_fraccion)
    
    def cargar_imagenes(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(script_dir, "assets")
            sonidos_dir = os.path.join(script_dir, "sonidos")
            
            # Cargar imágenes sin escalar (tamaño original)
            self.img_frente_original = pygame.image.load(os.path.join(assets_dir, "ficha2.png"))
            self.img_frente_v_original = pygame.image.load(os.path.join(assets_dir, "ficha2_v.png"))
            self.img_dorso_original = pygame.image.load(os.path.join(assets_dir, "dorso12.png"))
            self.img_dorso_v_original = pygame.image.load(os.path.join(assets_dir, "dorso12_v.png"))
            self.img_baa = pygame.image.load(os.path.join(assets_dir, "BAA2.png"))

            # Escalar al tamaño normal para la mano y tablero
            self.img_frente = pygame.transform.smoothscale(self.img_frente_original, (self.largo_ficha, self.ancho_ficha))
            self.img_frente_v = pygame.transform.smoothscale(self.img_frente_v_original, (self.ancho_ficha, self.largo_ficha))
            self.img_dorso = pygame.transform.smoothscale(self.img_dorso_original, (self.largo_ficha, self.ancho_ficha))
            self.img_dorso_v = pygame.transform.smoothscale(self.img_dorso_v_original, (self.ancho_ficha, self.largo_ficha))
            
            ruta_boton_robar = os.path.join(assets_dir, "boton_robar.png")
            ruta_boton_pasar = os.path.join(assets_dir, "boton_pasar.png")
            ruta_boton_reset = os.path.join(assets_dir, "boton_reset.png")
            ruta_boton_ayuda = os.path.join(assets_dir, "boton_ayuda.png")
            ruta_boton_lupa = os.path.join(assets_dir, "boton_lupa.png")
            
            self.img_boton_robar = pygame.image.load(ruta_boton_robar)
            self.img_boton_pasar = pygame.image.load(ruta_boton_pasar)
            self.img_boton_reset = pygame.image.load(ruta_boton_reset)
            self.img_boton_ayuda = pygame.image.load(ruta_boton_ayuda)
            self.img_boton_lupa = pygame.image.load(ruta_boton_lupa)

            print("✅ Imágenes cargadas correctamente")

            self.sonido_win = pygame.mixer.Sound(os.path.join(sonidos_dir, "win.mp3"))
            self.sonido_girar = pygame.mixer.Sound(os.path.join(sonidos_dir, "girar.mp3"))
            self.sonido_clic = pygame.mixer.Sound(os.path.join(sonidos_dir, "clic.mp3"))
            self.sonido_coin = pygame.mixer.Sound(os.path.join(sonidos_dir, "coin.mp3"))
            self.sonido_error = pygame.mixer.Sound(os.path.join(sonidos_dir, "error.mp3"))
            
            print("✅ Sonidos cargados correctamente")

        except Exception as e:
            print(f"⚠️ Error cargando imágenes: {e}")
            self.img_frente = None
            self.img_frente_v = None
            self.img_dorso = None
            self.img_boton_robar = None
            self.img_boton_pasar = None
            self.img_boton_reset = None
            self.img_boton_ayuda = None
            self.img_boton_lupa = None
            self.sonido_win = None
            self.sonido_girar = None
            self.sonido_clic = None
            self.sonido_coin = None
            self.sonido_error = None
            self.img_baa = None

    def calcular_offset_tablero(self):
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        for casilla in self.partida.tablero.casillas:
            if casilla.x < min_x:
                min_x = casilla.x
            if casilla.x + LARGO_FICHA > max_x:
                max_x = casilla.x + LARGO_FICHA
            if casilla.y < min_y:
                min_y = casilla.y
            if casilla.y + ANCHO_FICHA > max_y:
                max_y = casilla.y + ANCHO_FICHA
        
        centro_x = (min_x + max_x) / 2
        centro_y = (min_y + max_y) / 2
        
        offset_x = self.ancho_pantalla // 2 - int(centro_x * self.escala)
        offset_y = self.alto_pantalla // 2 - int(centro_y * self.escala)
        
        media_ficha = int((ANCHO_FICHA / 2) * self.escala)
        self.offset_tablero_x = offset_x + media_ficha
        self.offset_tablero_y = offset_y
    
    def crear_botones(self):
        self.botones = []
        
        alto_boton = int(50 * self.escala)
        ancho_boton = int(200 * self.escala)
        separacion = int(20 * self.escala)
        
        centro_x = self.ancho_pantalla // 2
        y_boton = self.alto_pantalla // 2 + int(220 * self.escala)
        
        self.boton_robar = Boton(
            centro_x - ancho_boton - separacion//2, 
            y_boton, 
            ancho_boton, 
            alto_boton, 
            "Robar del pozo",
            self.img_boton_robar
        )
        self.botones.append(self.boton_robar)
        
        self.boton_pasar = Boton(
            centro_x + separacion//2, 
            y_boton, 
            ancho_boton, 
            alto_boton, 
            "Pasar turno",
            self.img_boton_pasar
        )
        self.botones.append(self.boton_pasar)

        #x_reiniciar = int(30 * self.escala)
        #y_reiniciar = self.alto_pantalla - int(75 * self.escala)
        x_reiniciar = self.ancho_pantalla - int(150 * self.escala) - int(30 * self.escala)
        y_reiniciar = self.alto_pantalla - int(75 * self.escala)
        ancho_reiniciar = int(150 * self.escala)
        alto_reiniciar = int(50 * self.escala)
        
        self.boton_reiniciar = Boton(
            x_reiniciar,
            y_reiniciar,
            ancho_reiniciar,
            alto_reiniciar,
            "Reiniciar",
            self.img_boton_reset
        )
        self.botones.append(self.boton_reiniciar)

        x_ayuda = self.ancho_pantalla - int(150 * self.escala) - int(30 * self.escala)
        y_ayuda = self.alto_pantalla - int(120 * self.escala)
        ancho_ayuda = int(150 * self.escala)
        alto_ayuda = int(50 * self.escala)
        
        self.boton_ayuda = Boton(
            x_ayuda,
            y_ayuda,
            ancho_ayuda,
            alto_ayuda,
            "Ayuda",
            self.img_boton_ayuda
        )
        self.botones.append(self.boton_ayuda)

        # Botón LUPA
        x_lupa = self.ancho_pantalla - int(150 * self.escala) - int(30 * self.escala)
        y_lupa = self.alto_pantalla - int(165 * self.escala)
        ancho_lupa = int(150 * self.escala)
        alto_lupa = int(50 * self.escala)

        self.boton_lupa = Boton(
            x_lupa,
            y_lupa,
            ancho_lupa,
            alto_lupa,
            "Lupa",
            self.img_boton_lupa
        )
        self.botones.append(self.boton_lupa)

    
    def actualizar_botones(self):
        partida = self.partida
        jugador = partida.jugador_actual()
        ya_robo = partida.ya_robo_en_turno
        puede_robar = partida.puede_robar(jugador)
        
        self.boton_robar.activo = not ya_robo and puede_robar and not partida.terminada
        self.boton_robar.activo = not ya_robo and puede_robar and not partida.terminada and self.ficha_inicial_colocada
        self.boton_pasar.activo = ya_robo and not partida.terminada
        self.boton_reiniciar.activo = True
        self.boton_ayuda.activo = True
        self.boton_lupa.activo = True

    def actualizar_posiciones_fichas(self):
        self.posiciones_fichas = {
            "jugador1": [],
            "jugador2": []
        }
        
        margen = int(30 * self.escala)
        y_inicial = int(80 * self.escala)
        max_por_columna = 11
        separacion = int(8 * self.escala)
        separacion_columnas = int(15 * self.escala)
        
        espacio_fijo_alto = self.ancho_ficha + separacion
        espacio_fijo_ancho = self.largo_ficha + separacion + separacion_columnas
        
        def calcular_posicion_ficha(ficha, i, x_base, direccion):
            if ficha == self.ficha_arrastrada:
                return None
            
            if ficha.orientacion == "horizontal":
                ancho = self.largo_ficha
                alto = self.ancho_ficha
            else:
                ancho = self.ancho_ficha
                alto = self.largo_ficha
            
            fila = i % max_por_columna
            columna = i // max_por_columna
            
            if direccion == "izquierda":
                x = x_base + columna * espacio_fijo_ancho
            else:
                x = x_base - columna * espacio_fijo_ancho
            
            y = y_inicial + fila * espacio_fijo_alto
            
            if ficha.orientacion == "vertical":
                x = x + (self.largo_ficha - self.ancho_ficha) // 2
            
            return {
                "ficha": ficha,
                "x": x,
                "y": y,
                "ancho": ancho,
                "alto": alto
            }
        
        for i, ficha in enumerate(self.partida.jugadores[0].fichas):
            pos = calcular_posicion_ficha(ficha, i, margen, "izquierda")
            if pos:
                self.posiciones_fichas["jugador1"].append(pos)
        
        x_derecha = self.ancho_pantalla - margen - self.largo_ficha
        for i, ficha in enumerate(self.partida.jugadores[1].fichas):
            pos = calcular_posicion_ficha(ficha, i, x_derecha, "derecha")
            if pos:
                self.posiciones_fichas["jugador2"].append(pos)


    def dibujar_valores_ficha(self, ficha, x, y, ancho, alto, factor=1.0):
        s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        s.fill((255, 255, 255, 180))
        self.pantalla.blit(s, (x, y))
        
        espacio_al_borde = int(5*factor)
        grosor_linea = int(2*factor)

        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (80, 80, 80), 
                           (x + ancho//2, y + espacio_al_borde), 
                           (x + ancho//2, y + alto - espacio_al_borde), grosor_linea)
        else:
            pygame.draw.line(self.pantalla, (80, 80, 80), 
                           (x + espacio_al_borde, y + alto//2), 
                           (x + ancho - espacio_al_borde, y + alto//2), grosor_linea)
        
        tamano_fuente_base = int(self.tamano_fuente_fraccion * factor)
        
        # Ancho disponible depende de la orientación
        if ficha.orientacion == "horizontal":
            # Dos mitades a lo ancho
            ancho_disponible = (ancho // 2) - int(10 * factor)
        else:
            # Dos mitades a lo alto
            ancho_disponible = ancho - int(10 * factor)

        def dibujar_fraccion(texto, x_centro, y_centro):
            if "\n" in texto:
                num, den = texto.split("\n")
            else:
                num = texto
                den = None
            
            # Calcular el tamaño de fuente necesario para que entre
            tamano_fuente = tamano_fuente_base
            fuente_prueba = pygame.font.Font(self.ruta_fuente, tamano_fuente)
            
            ancho_num = fuente_prueba.size(num)[0] if num else 0
            ancho_den = fuente_prueba.size(den)[0] if den else 0
            ancho_max = max(ancho_num, ancho_den)
            
            if ancho_max > ancho_disponible and ancho_max > 0:
                factor_ajuste = ancho_disponible / ancho_max
                tamano_fuente = int(tamano_fuente_base * factor_ajuste)
                if tamano_fuente < 8:
                    tamano_fuente = 8
                fuente_prueba = pygame.font.Font(self.ruta_fuente, tamano_fuente)
            
            fuente_escalada = fuente_prueba
            
            texto_num = fuente_escalada.render(num, True, (0, 0, 0)) if num else None
            texto_den = fuente_escalada.render(den, True, (0, 0, 0)) if den else None
            
            if den is None:
                if texto_num:
                    self.pantalla.blit(texto_num, 
                        (x_centro - texto_num.get_width() // 2, 
                         y_centro - texto_num.get_height() // 2))
                return
            
            alto_num = texto_num.get_height() if texto_num else 0
            alto_den = texto_den.get_height() if texto_den else 0
            
            proporcion = tamano_fuente / tamano_fuente_base
            separacion_entre_lineas = int(-5 * proporcion)
            #separacion_entre_lineas = -5*factor
            
            ancho_num = texto_num.get_width() if texto_num else 0
            ancho_den = texto_den.get_width() if texto_den else 0
            ancho_max = max(ancho_num, ancho_den)
            
            ancho_linea = int(ancho_max * 1)
            alto_linea = max(1, int(2 * proporcion))
            #alto_linea = 2*factor
            
            alto_total = alto_num + alto_den + separacion_entre_lineas + alto_linea
            
            y_inicio = y_centro - alto_total // 2
            
            if texto_num:
                self.pantalla.blit(texto_num, 
                    (x_centro - texto_num.get_width() // 2, 
                     y_inicio))
            
            y_linea = y_inicio + alto_num + separacion_entre_lineas // 2
            pygame.draw.rect(self.pantalla, (0, 0, 0), 
                            (x_centro - ancho_linea // 2, y_linea, ancho_linea, alto_linea))
            
            if texto_den:
                y_den = y_linea + alto_linea + separacion_entre_lineas // 2
                self.pantalla.blit(texto_den, 
                    (x_centro - texto_den.get_width() // 2, 
                     y_den))
        
        if ficha.orientacion == "horizontal":
            dibujar_fraccion(ficha.textos["O"], x + ancho//4, y + alto//2)
            dibujar_fraccion(ficha.textos["E"], x + 3 * ancho//4, y + alto//2)
        else:
            dibujar_fraccion(ficha.textos["N"], x + ancho//2, y + alto//4)
            dibujar_fraccion(ficha.textos["S"], x + ancho//2, y + 3 * alto//4)

    
    def dibujar_ficha_tablero(self, ficha, x, y, ancho, alto, resaltada=False):
        if self.img_frente is not None:
            if ficha.orientacion == "vertical":
                img = pygame.transform.scale(self.img_frente_v, (ancho, alto))
            else:
                img = pygame.transform.scale(self.img_frente, (ancho, alto))

            self.pantalla.blit(img, (x, y))
            
            if resaltada:
                pygame.draw.rect(self.pantalla, (50, 255, 50), (x, y, ancho, alto), 
                               max(2, int(4 * self.escala)), border_radius=5)
            
            self.dibujar_valores_ficha(ficha, x, y, ancho, alto)
            return
        
        color = (240, 240, 240)
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), 2, border_radius=5)
        
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + ancho//2, y + 5), (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + 5, y + alto//2), (x + ancho - 5, y + alto//2), 2)
        
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente_fraccion.render(ficha.textos["O"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["E"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + int(10 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
            self.pantalla.blit(texto2, (x + ancho - int(30 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + int(10 * self.escala)))
            self.pantalla.blit(texto2, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + alto - int(30 * self.escala)))
    
    def dibujar_ficha_dorso(self, x, y, ancho, alto, orientacion="horizontal"):
        if orientacion == "vertical" and self.img_dorso_v is not None:
            self.pantalla.blit(self.img_dorso_v, (x, y))
        elif self.img_dorso is not None:
            self.pantalla.blit(self.img_dorso, (x, y))
        else:
            pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), border_radius=5)
            pygame.draw.rect(self.pantalla, (50, 50, 50), (x, y, ancho, alto), 2, border_radius=5)

    def dibujar_ficha_mano(self, ficha, x, y, seleccionada=False, jugador=None, es_turno=False):
        mostrar_frente = False
        
        if not self.ficha_inicial_colocada:
            if jugador == self.jugador_inicial and ficha == self.ficha_inicial:
                mostrar_frente = True
        else:
            if es_turno:
                mostrar_frente = True
        
        if mostrar_frente:
            if ficha.orientacion == "horizontal":
                ancho = self.largo_ficha
                alto = self.ancho_ficha
                dx = 0
                dy = 0
            else:
                ancho = self.ancho_ficha
                alto = self.largo_ficha
                dx = 0
                dy = (self.ancho_ficha - self.largo_ficha) // 2
            
            if self.img_frente is not None:
                img = self.img_frente_v if ficha.orientacion == "vertical" else self.img_frente
                self.pantalla.blit(img, (x + dx, y + dy))
                
                if seleccionada:
                    pygame.draw.rect(self.pantalla, (100, 200, 255), (x + dx, y + dy, ancho, alto), 
                                   max(2, int(4 * self.escala)), border_radius=5)
                
                self.dibujar_valores_ficha(ficha, x + dx, y + dy, ancho, alto)
                return
        else:
            if ficha.orientacion == "horizontal":
                ancho = self.largo_ficha
                alto = self.ancho_ficha
            else:
                ancho = self.ancho_ficha
                alto = self.largo_ficha
            
            if self.img_dorso is not None:
                img = self.img_dorso_v if ficha.orientacion == "vertical" else self.img_dorso
                self.pantalla.blit(img, (x, y))
                return

    def dibujar_ficha_arrastrada(self, ficha, x, y):
        factor = 2
        if ficha.orientacion == "horizontal":
            ancho = self.largo_ficha
            alto = self.ancho_ficha
            dx = 0
            dy = 0
        else:
            ancho = self.ancho_ficha
            alto = self.largo_ficha
            dx = (self.largo_ficha - self.ancho_ficha) // 2
            dy = (self.ancho_ficha - self.largo_ficha) // 2
        
        ancho, alto = ancho*factor, alto*factor
        dx, dy = dx*factor, dy*factor

        if self.img_frente is not None:
            if ficha.orientacion == "vertical":
                img = self.img_frente_v_original
            else:
                img = self.img_frente_original
            img = pygame.transform.scale(img, (ancho, alto))

            self.pantalla.blit(img, (x + dx, y + dy))
            
            #pygame.draw.rect(self.pantalla, (200, 255, 200), (x + dx, y + dy, ancho, alto), 
            #               max(2, int(4 * self.escala)), border_radius=5)
            
            self.dibujar_valores_ficha(ficha, x + dx, y + dy, ancho, alto, factor=factor)
            return
        
        color = (200, 255, 200)
        pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), border_radius=5)
        pygame.draw.rect(self.pantalla, (100, 100, 100), (x, y, ancho, alto), 2, border_radius=5)
        
        if ficha.orientacion == "horizontal":
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + ancho//2, y + 5), (x + ancho//2, y + alto - 5), 2)
        else:
            pygame.draw.line(self.pantalla, (100, 100, 100), 
                           (x + 5, y + alto//2), (x + ancho - 5, y + alto//2), 2)
        
        if ficha.orientacion == "horizontal":
            texto1 = self.fuente_fraccion.render(ficha.textos["O"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["E"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + int(10 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
            self.pantalla.blit(texto2, (x + ancho - int(30 * self.escala), y + alto//2 - self.tamano_fuente_fraccion//2))
        else:
            texto1 = self.fuente_fraccion.render(ficha.textos["N"].replace("/", "|"), True, (0, 0, 0))
            texto2 = self.fuente_fraccion.render(ficha.textos["S"].replace("/", "|"), True, (0, 0, 0))
            self.pantalla.blit(texto1, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + int(10 * self.escala)))
            self.pantalla.blit(texto2, (x + ancho//2 - self.tamano_fuente_fraccion//2, y + alto - int(30 * self.escala)))

    def dibujar_pozo(self):
        fichas_pozo = self.partida.pozo.fichas
        if not fichas_pozo:
            return
        
        centro_x = self.ancho_pantalla // 2
        centro_y = self.alto_pantalla // 2
        
        por_fila = 6
        separacion = int(5 * self.escala)
        ancho = self.ancho_ficha
        alto = self.largo_ficha
        
        total_ancho = por_fila * (ancho + separacion)
        total_alto = (len(fichas_pozo) // por_fila + 1) * (alto + separacion)
        
        inicio_x = centro_x - total_ancho // 2
        inicio_y = centro_y - total_alto // 2
        
        max_mostrar = 30
        for i in range(min(len(fichas_pozo), max_mostrar)):
            fila = i // por_fila
            columna = i % por_fila
            
            x = inicio_x + columna * (ancho + separacion)
            y = inicio_y + fila * (alto + separacion)
            
            ficha = fichas_pozo[i]
            self.dibujar_ficha_dorso(x, y, ancho, alto, 'vertical')
        
        texto = self.fuente.render(f"Pozo: {len(fichas_pozo)} fichas", True, (200, 200, 200))
        self.pantalla.blit(texto, (centro_x - texto.get_width() // 2, inicio_y - int(30 * self.escala)))

    def dibujar_tablero(self):
        for casilla in self.partida.tablero.casillas:
            x = int(casilla.x * self.escala) + self.offset_tablero_x
            y = int(casilla.y * self.escala) + self.offset_tablero_y
            
            if casilla.ficha is not None:
                if casilla.orientacion == "horizontal":
                    ancho = self.largo_ficha
                    alto = self.ancho_ficha
                else:
                    ancho = self.ancho_ficha
                    alto = self.largo_ficha
                
                destacada = casilla in self.casillas_destacadas
                
                self.dibujar_ficha_tablero(
                    casilla.ficha,
                    x, y,
                    ancho, alto,
                    resaltada=destacada
                )
            else:
                if casilla.orientacion == "horizontal":
                    ancho = self.largo_ficha
                    alto = self.ancho_ficha
                else:
                    ancho = self.ancho_ficha
                    alto = self.largo_ficha
                
                if casilla in self.casillas_destacadas:
                    color = COLOR_CASILLA_DESTACADA
                    grosor = 0
                    pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto))
                else:
                    color = COLOR_CASILLA_VACIA
                    grosor = 2
                    pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), grosor)
                pygame.draw.rect(self.pantalla, color, (x, y, ancho, alto), grosor)

    def obtener_ficha_en_posicion(self, x, y):
        partida = self.partida
        jugador_actual = partida.jugador_actual()
        
        if partida.ya_robo_en_turno and self.ficha_robada_actual is not None:
            for pos in self.posiciones_fichas["jugador1"] + self.posiciones_fichas["jugador2"]:
                if pos["ficha"] == self.ficha_robada_actual:
                    if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                        pos["y"] <= y <= pos["y"] + pos["alto"]):
                        return self.ficha_robada_actual, jugador_actual
            return None, None
        
        for pos in self.posiciones_fichas["jugador1"]:
            if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                pos["y"] <= y <= pos["y"] + pos["alto"]):
                return pos["ficha"], self.partida.jugadores[0]
        
        for pos in self.posiciones_fichas["jugador2"]:
            if (pos["x"] <= x <= pos["x"] + pos["ancho"] and
                pos["y"] <= y <= pos["y"] + pos["alto"]):
                return pos["ficha"], self.partida.jugadores[1]
        
        return None, None
    
    def obtener_casilla_en_posicion(self, x, y):
        x_ajustada = (x - self.offset_tablero_x) / self.escala
        y_ajustada = (y - self.offset_tablero_y) / self.escala
        
        for casilla in self.partida.tablero.casillas:
            if casilla.orientacion == "horizontal":
                ancho = LARGO_FICHA
                alto = ANCHO_FICHA
            else:
                ancho = ANCHO_FICHA
                alto = LARGO_FICHA
            
            if (casilla.x <= x_ajustada <= casilla.x + ancho and
                casilla.y <= y_ajustada <= casilla.y + alto):
                return casilla
        
        return None

    def actualizar_casillas_destacadas(self, ficha, jugador):
        self.casillas_destacadas = []
        if ficha is None:
            return
        
        x, y = pygame.mouse.get_pos()
        casilla_bajo_mouse = self.obtener_casilla_en_posicion(x, y)
        
        if casilla_bajo_mouse is None:
            return
        
        if casilla_bajo_mouse.ficha is not None:
            return
        
        if jugador == self.partida.jugador_actual():
            if self.partida.tablero.primera_jugada:
                if casilla_bajo_mouse.orientacion == ficha.orientacion:
                    self.casillas_destacadas.append(casilla_bajo_mouse)
            else:
                head = self.partida.tablero.head_posible.casilla
                tail = self.partida.tablero.tail_posible.casilla
                if casilla_bajo_mouse.numero == head.numero or casilla_bajo_mouse.numero == tail.numero:
                    if casilla_bajo_mouse.orientacion == ficha.orientacion:
                        self.casillas_destacadas.append(casilla_bajo_mouse)

    def verificar_y_mostrar_fin_partida(self):
        if self.partida.terminada:
            if self.partida.ganador:
                if self.partida.ganador == self.partida.jugadores[0]:
                    color = COLOR_JUGADOR1
                    nombre = self.nombre_jugador1
                else:
                    color = COLOR_JUGADOR2
                    nombre = self.nombre_jugador2
                if self.sonido_win:
                    self.sonido_win.play()
                self.mostrar_mensaje(f"¡{nombre} GANÓ!", "success", color)
            else:
                self.mostrar_mensaje("EMPATE", "warning")
            self.actualizar_botones()
            return True
        
        self.partida.verificar_fin_partida()
        if self.partida.terminada:
            if self.partida.ganador:
                if self.partida.ganador == self.partida.jugadores[0]:
                    color = COLOR_JUGADOR1
                    nombre = self.nombre_jugador1
                else:
                    color = COLOR_JUGADOR2
                    nombre = self.nombre_jugador2
                self.mostrar_mensaje(f"¡{nombre} GANÓ!", "success", color)
            else:
                self.mostrar_mensaje("EMPATE", "warning")
            self.actualizar_botones()
            return True
        
        return False

    def mostrar_mensaje(self, texto, tipo="info", color=None, visible=False):
        if visible:
            self.mensaje = texto
            self.tiempo_mensaje = pygame.time.get_ticks()
            if color:
                self.mensaje_color = color
            else:
                self.mensaje_color = COLOR_TEXTO
        # Si no es visible, no guarda nada

    '''
    def mostrar_mensaje(self, texto, tipo="info", color=None):
        self.mensaje = texto
        self.tiempo_mensaje = pygame.time.get_ticks()
        if color:
            self.mensaje_color = color
        else:
            self.mensaje_color = COLOR_TEXTO
    '''

    def dibujar_mensajes(self):
        centro_x = self.ancho_pantalla // 2
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_fuente = os.path.join(script_dir, "fonts", archivofuente)
        
        titulo_linea1 = self.fuente_grande.render("Dominó de", True, COLOR_TITULO)
        titulo_linea2 = self.fuente_grande.render("expresiones decimales", True, COLOR_TITULO)

        y_titulo = int(140 * self.escala)
        alto_linea = titulo_linea1.get_height()

        # Línea 1
        ancho_t1 = titulo_linea1.get_width()
        self.pantalla.blit(titulo_linea1, (centro_x - ancho_t1//2, y_titulo - alto_linea//2))

        # Línea 2 (debajo de la línea 1)
        ancho_t2 = titulo_linea2.get_width()
        self.pantalla.blit(titulo_linea2, (centro_x - ancho_t2//2, y_titulo + alto_linea//4))

        #titulo = self.fuente_grande.render("Dominó de expresiones decimales", True, COLOR_TITULO)
        #y_titulo = int(150 * self.escala)
        
        #ancho_t = titulo.get_width()
        #alto_t = titulo.get_height()
        #self.pantalla.blit(titulo, (centro_x - ancho_t//2, y_titulo - alto_t//2))
        
        # --- NUEVO: Verificar si hay mensaje temporal ---
        hay_mensaje_temporal = False
        if self.mensaje and (pygame.time.get_ticks() - self.tiempo_mensaje < 1500):
            hay_mensaje_temporal = True
        elif self.mensaje:
            # Pasaron más de 2 segundos, borrar el mensaje
            self.mensaje = ""

        if hay_mensaje_temporal:
            texto = self.mensaje
            color = self.mensaje_color
        elif self.partida.terminada:
            if self.partida.ganador:
                if self.partida.ganador == self.partida.jugadores[0]:
                    color = COLOR_JUGADOR1
                    nombre = self.nombre_jugador1
                else:
                    color = COLOR_JUGADOR2
                    nombre = self.nombre_jugador2
                texto = f"¡{nombre} GANÓ!"
            else:
                color = COLOR_TEXTO
                texto = "EMPATE"
        else:
            jugador_actual = self.partida.jugador_actual()
            if jugador_actual == self.partida.jugadores[0]:
                color = COLOR_JUGADOR1
                nombre = self.nombre_jugador1
            else:
                color = COLOR_JUGADOR2
                nombre = self.nombre_jugador2
            texto = f"Turno: {nombre}"
        
        texto_turno = self.fuente_grande.render(texto, True, color)
        y_turno = y_titulo + int(400 * self.escala)
        ancho_turno = texto_turno.get_width()
        alto_turno = texto_turno.get_height()
        self.pantalla.blit(texto_turno, (centro_x - ancho_turno//2, y_turno - alto_turno//2))

    def dibujar_ayuda(self):
        x = self.ancho_pantalla - int(300 * self.escala)
        y = self.alto_pantalla - int(100 * self.escala)
        
        lineas = ["ESC: Salir"]
        
        for i, linea in enumerate(lineas):
            texto = self.fuente.render(linea, True, (150, 150, 150))
            self.pantalla.blit(texto, (x, y + i * int(25 * self.escala)))

    def reiniciar_partida(self):
        # Crear nueva partida
        self.partida = Partida("fichas2.csv", fichas_por_jugador=6)
        self.ficha_inicial, self.jugador_inicial = self.partida.determinar_ficha_inicial()
        self.ficha_inicial_colocada = False
        
        # Resetear estado del juego
        self.ficha_seleccionada = None
        self.ficha_arrastrada = None
        self.ficha_robada_actual = None
        self.ficha_clickeada = None
        self.casillas_destacadas = []
        self.mensaje = ""
        self.tiempo_mensaje = 0
        self.offset_x = 0
        self.offset_y = 0
        
        self.calcular_offset_tablero()
        self.actualizar_posiciones_fichas()
        self.actualizar_botones()
        
        # Reasignar nombres
        self.partida.jugadores[0].nombre = self.nombre_jugador1
        self.partida.jugadores[1].nombre = self.nombre_jugador2
        
        # Forzar volver a la pantalla de input
        self.volver_a_input = True
        self.nombres_ingresados = False
        self.ingresando_nombre = 0

        # FORZAR EL TURNO AL JUGADOR QUE COMIENZA
        self.partida.turno = self.partida.jugadores.index(self.jugador_inicial)
        
        self.mostrar_mensaje("Partida reiniciada")
    

    def dibujar_confirmacion_reinicio(self):
        if not self.mostrar_confirmacion_reinicio and not self.mostrar_confirmacion_salir:
            return
        
        s = pygame.Surface((self.ancho_pantalla, self.alto_pantalla), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))
        
        ancho_cartel = int(550 * self.escala)
        alto_cartel = int(180 * self.escala)
        x_cartel = (self.ancho_pantalla - ancho_cartel) // 2
        y_cartel = (self.alto_pantalla - alto_cartel) // 2
        
        pygame.draw.rect(self.pantalla, (50, 50, 50), (x_cartel, y_cartel, ancho_cartel, alto_cartel), border_radius=10)
        pygame.draw.rect(self.pantalla, (150, 150, 150), (x_cartel, y_cartel, ancho_cartel, alto_cartel), 2, border_radius=10)
        
        if self.mostrar_confirmacion_salir:
            texto = self.fuente_grande.render("¿Querés salir del juego?", True, (255, 255, 255))
        else:
            texto = self.fuente_grande.render(self.mensaje_confirmacion, True, (255, 255, 255))
        
        self.pantalla.blit(texto, (self.ancho_pantalla // 2 - texto.get_width() // 2, 
                                  y_cartel + int(30 * self.escala)))
        
        instrucciones = self.fuente.render("Presioná S para Sí, N para No", True, (200, 200, 200))
        self.pantalla.blit(instrucciones, (self.ancho_pantalla // 2 - instrucciones.get_width() // 2, 
                                          y_cartel + int(110 * self.escala)))

    def dibujar_ayuda_cartel(self):
        if not self.mostrar_ayuda:
            return
        
        s = pygame.Surface((self.ancho_pantalla, self.alto_pantalla), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.pantalla.blit(s, (0, 0))
        
        ancho_cartel = int(950 * self.escala)
        alto_cartel = int(600 * self.escala)
        x_cartel = (self.ancho_pantalla - ancho_cartel) // 2
        y_cartel = (self.alto_pantalla - alto_cartel) // 2
        
        pygame.draw.rect(self.pantalla, (50, 50, 50), (x_cartel, y_cartel, ancho_cartel, alto_cartel), border_radius=10)
        pygame.draw.rect(self.pantalla, (150, 150, 150), (x_cartel, y_cartel, ancho_cartel, alto_cartel), 2, border_radius=10)
        
        titulo = self.fuente_grande.render("Instrucciones", True, (255, 255, 255))
        self.pantalla.blit(titulo, (self.ancho_pantalla // 2 - titulo.get_width() // 2, y_cartel + int(5 * self.escala)))
        
        pygame.draw.line(self.pantalla, (150, 150, 150), 
                        (x_cartel + int(20 * self.escala), y_cartel + int(50 * self.escala)),
                        (x_cartel + ancho_cartel - int(20 * self.escala), y_cartel + int(50 * self.escala)), 1)
        
        fuente_instrucciones = pygame.font.Font(self.ruta_fuente, int(22 * self.escala))
    
 

#Gana el jugador que se quede sin fichas primero. Si un jugador no puede colocar y el pozo está vacío, pierde.

        instrucciones = [
            "1. Cada jugador recibe 6 fichas. Comienza el jugador que tenga la mayor ficha con dos",
            "expresiones equivalentes.",
            "",
            "2. En su turno, cada jugador debe colocar una ficha que tenga un número equivalente al",
            "que aparece en alguno de los extremos de la cadena. Podés girar una ficha haciendo clic",
            "sobre ella o con la tecla G.",
            "",
            "3. Si no podés ubicar ninguna ficha, debés robar una ficha del pozo (botón celeste). Si la",
            "ficha robada sirve, podés colocarla. Si no sirve, tenés que pasar el turno (botón verde).",
            "",
            "4. Final del juego: gana el jugador que se quede sin fichas primero. Si un jugador no puede",
            "colocar y el pozo está vacío, pierde.",
            "",
            "¡Atención! Si jugás una ficha que no encaja, perdés tu turno."
        ]

        creditos = [
            "Territorio de Juegos - Escuelas en Foco Matemática",
            "Coordinación general: Gloria Rodríguez",
            "Diseño y desarrollo: Andrea Pallai y Ernesto López"
        ]

        y_texto = y_cartel + int(70 * self.escala)
        for linea in instrucciones:
            texto = fuente_instrucciones.render(linea, True, (220, 220, 220))
            self.pantalla.blit(texto, (x_cartel + int(25 * self.escala), y_texto))
            y_texto += int(25 * self.escala)
        
        # Separador y desarrollador
        y_texto += int(10 * self.escala)
        pygame.draw.line(self.pantalla, (100, 100, 100), 
                        (x_cartel + int(20 * self.escala), y_texto),
                        (x_cartel + ancho_cartel - int(20 * self.escala), y_texto), 1)
        y_texto += int(20 * self.escala)
        
        for linea in creditos:
            L = self.fuente.render(linea, True, COLOR_TITULO)
            self.pantalla.blit(L, (self.ancho_pantalla // 2 - L.get_width() // 2, y_texto))
            y_texto += int(28 * self.escala)

        cerrar = self.fuente.render("Presioná la tecla enter para cerrar", True, (150, 150, 150))
        self.pantalla.blit(cerrar, (self.ancho_pantalla // 2 - cerrar.get_width() // 2, y_cartel + alto_cartel - int(35 * self.escala)))

    async def ejecutar(self):
        juego_activo = True
        
        while juego_activo:
            # --- INPUT DE NOMBRES ---
            if not await self.bucle_input_nombres():
                break
            
            # --- MOSTRAR MENSAJE DE QUIÉN COMIENZA ---
            self.mostrar_mensaje_inicio()
            
            # --- BUCLE DEL JUEGO ---
            if not await self.bucle_juego():
                # Si salió del juego, verificar si fue por reinicio o por cierre
                if self.nombres_ingresados == False:
                    # Reinicio: continuar el bucle externo para volver al input
                    continue
                else:
                    # Cierre: salir del bucle externo
                    break
            
        pygame.quit()
        return

    async def bucle_input_nombres(self):
        """Maneja la pantalla de ingreso de nombres. Retorna False si se cierra."""
        self.ingresando_nombre = 0
        while not self.nombres_ingresados:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    self.procesar_click_input(evento)
                
                elif evento.type == pygame.KEYDOWN:
                    if not self.procesar_tecla_input(evento):
                        return False
            
            self.dibujar_input_nombres()
            self.dibujar_confirmacion_reinicio()
            pygame.display.flip()
            await asyncio.sleep(1 / 60)
        
        return True

    def procesar_click_input(self, evento):
        """Procesa clics en la pantalla de input"""
        x, y = evento.pos
        centro_x = self.ancho_pantalla // 2
        centro_y = self.alto_pantalla // 2
        
        rect_j1 = pygame.Rect(centro_x - 80, centro_y - 210, 350, 80)
        rect_j2 = pygame.Rect(centro_x - 80, centro_y - 115, 350, 80)
        
        if rect_j1.collidepoint(x, y):
            self.ingresando_nombre = 1
            self.nombre_jugador1 = ""
        elif rect_j2.collidepoint(x, y):
            self.ingresando_nombre = 2
            self.nombre_jugador2 = ""
        else:
            self.ingresando_nombre = 0

    def procesar_tecla_input(self, evento):
        """Procesa teclas en la pantalla de input. Retorna False si se cierra."""
        # Si el cartel de salir está abierto
        if self.mostrar_confirmacion_salir:
            if evento.key == pygame.K_s:
                return False
            elif evento.key == pygame.K_n:
                self.mostrar_confirmacion_salir = False
                return True
            return True
        
        if evento.key == pygame.K_RETURN or evento.key == pygame.K_KP_ENTER:
            if len(self.nombre_jugador1.strip()) > 0 and len(self.nombre_jugador2.strip()) > 0:
                pygame.mixer.music.stop()
                self.nombres_ingresados = True
                self.crear_partida_con_nombres()
        elif evento.key == pygame.K_BACKSPACE:
            if self.ingresando_nombre == 1:
                self.nombre_jugador1 = self.nombre_jugador1[:-1]
            elif self.ingresando_nombre == 2:
                self.nombre_jugador2 = self.nombre_jugador2[:-1]
        elif evento.key == pygame.K_ESCAPE:
            self.mostrar_confirmacion_salir = True
        else:
            if self.ingresando_nombre == 1:
                self.nombre_jugador1 += evento.unicode
            elif self.ingresando_nombre == 2:
                self.nombre_jugador2 += evento.unicode
        
        return True

    def crear_partida_con_nombres(self):
        """Crea la partida con los nombres ingresados"""
        self.partida = Partida("fichas2.csv", fichas_por_jugador=6)
        self.partida.jugadores[0].nombre = self.nombre_jugador1
        self.partida.jugadores[1].nombre = self.nombre_jugador2
        self.ficha_inicial, self.jugador_inicial = self.partida.determinar_ficha_inicial()
        self.ficha_inicial_colocada = False
        self.partida.turno = self.partida.jugadores.index(self.jugador_inicial)
        self.calcular_offset_tablero()
        self.actualizar_posiciones_fichas()
        self.actualizar_botones()

    def mostrar_mensaje_inicio(self):
        """Muestra quién comienza la partida"""
        if self.jugador_inicial == self.partida.jugadores[0]:
            nombre = self.nombre_jugador1
            color = COLOR_JUGADOR1
        else:
            nombre = self.nombre_jugador2
            color = COLOR_JUGADOR2
        self.mostrar_mensaje(f"Comienza {nombre}!", "info", color)

    def dibujar_logo_baa(self):
        escala_baa = 0.25 * self.escala
        ancho_baa = int(self.img_baa.get_width() * escala_baa)
        alto_baa = int(self.img_baa.get_height() * escala_baa)
        img_baa = pygame.transform.smoothscale(self.img_baa,(ancho_baa, alto_baa))
        margenx, margeny = int(20 * self.escala) , int(30 * self.escala)
        x = margenx
        y = self.alto_pantalla - alto_baa - margeny
        self.pantalla.blit(img_baa, (x, y))

    async def bucle_juego(self):
        """Bucle principal del juego. Retorna False si se cierra."""
        ejecutando = True
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return False
                
                elif evento.type == pygame.KEYDOWN:
                    if not self.procesar_tecla_juego(evento):
                        return False
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    self.procesar_click_juego(evento)
                
                elif evento.type == pygame.MOUSEMOTION:
                    self.procesar_motion_juego(evento)
                
                elif evento.type == pygame.MOUSEBUTTONUP:
                    self.procesar_soltar_ficha(evento)
            
            self.dibujar_juego()
            pygame.display.flip()
            await asyncio.sleep(1 / 60)
        
        return True

    def procesar_tecla_juego(self, evento):
        """Procesa teclas en el juego. Retorna False si se cierra."""
        if self.mostrar_ayuda:
            self.mostrar_ayuda = False
            return True
        
        if evento.key == pygame.K_ESCAPE:
            if self.mostrar_confirmacion_reinicio:
                self.mostrar_confirmacion_reinicio = False
                self.mensaje_confirmacion = ""
            elif self.mostrar_confirmacion_salir:
                pass
            else:
                self.mostrar_confirmacion_salir = True
            return True
        
        if evento.key == pygame.K_s:
            if self.mostrar_confirmacion_reinicio:
                self.reiniciar_partida()
                self.mostrar_confirmacion_reinicio = False
                self.mensaje_confirmacion = ""
                self.nombres_ingresados = False
                return False  # Salir del bucle para volver al input
            elif self.mostrar_confirmacion_salir:
                return False  # Salir del juego
        
        if evento.key == pygame.K_n:
            if self.mostrar_confirmacion_reinicio:
                self.mostrar_confirmacion_reinicio = False
                self.mensaje_confirmacion = ""
            elif self.mostrar_confirmacion_salir:
                self.mostrar_confirmacion_salir = False
            return True
        
        if evento.key == pygame.K_g:
            if self.ficha_seleccionada is not None and not self.partida.terminada:
                self.ficha_seleccionada.girar_90()
                if self.sonido_girar:
                    self.sonido_girar.play()
                self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_seleccionada.mostrar_valores()}")
                self.actualizar_posiciones_fichas()
                self.actualizar_botones()
        
        return True

    def procesar_click_juego(self, evento):
        """Procesa clics en el juego"""
        if evento.button != 1:
            return
        
        x, y = evento.pos
        
        # Botones
        for boton in self.botones:
            if boton.click():
                if boton == self.boton_robar:
                    self.ejecutar_robar()
                elif boton == self.boton_pasar:
                    self.ejecutar_pasar()
                elif boton == self.boton_reiniciar:
                    self.mostrar_confirmacion_reinicio = True
                    self.mensaje_confirmacion = "¿Reiniciar partida?"
                elif boton == self.boton_ayuda:
                    self.mostrar_ayuda = not self.mostrar_ayuda
                elif boton == self.boton_lupa:
                    self.mostrar_lupa = True
                    self.tiempo_lupa = pygame.time.get_ticks()
                    if self.sonido_clic:
                        self.sonido_clic.play()
                return
        
        # Seleccionar ficha
        ficha, jugador = self.obtener_ficha_en_posicion(x, y)
        if ficha is not None and jugador == self.partida.jugador_actual() and not self.partida.terminada:
            if not self.ficha_inicial_colocada and jugador == self.jugador_inicial:
                if ficha == self.ficha_inicial:
                    self.ficha_clickeada = ficha
                    self.pos_click_x = x
                    self.pos_click_y = y
                    self.ficha_arrastrada = None
                    self.ficha_seleccionada = ficha
            else:
                self.ficha_clickeada = ficha
                self.pos_click_x = x
                self.pos_click_y = y
                self.ficha_arrastrada = None
                self.ficha_seleccionada = ficha

    def ejecutar_robar(self):
        """Ejecuta la acción de robar del pozo"""
        if not self.partida.ya_robo_en_turno and not self.partida.terminada and self.ficha_inicial_colocada:
            ficha = self.partida.robar_ficha()
            if ficha:
                if self.sonido_clic:
                    self.sonido_clic.play()
                self.ficha_robada_actual = ficha
                self.ficha_seleccionada = ficha
                self.mostrar_mensaje(f"📥 {self.partida.jugador_actual().nombre} robó: {ficha.mostrar_valores()}")
                self.actualizar_posiciones_fichas()
                self.actualizar_botones()
            else:
                self.mostrar_mensaje("❌ No hay fichas en el pozo")

    def ejecutar_pasar(self):
        """Ejecuta la acción de pasar turno"""
        if self.partida.ya_robo_en_turno and not self.partida.terminada:
            if self.sonido_clic:
                self.sonido_clic.play()
            self.partida.pasar_turno()
            self.mostrar_mensaje(f"⏭️ {self.partida.jugador_actual().nombre} pasa turno")
            self.ficha_seleccionada = None
            self.ficha_arrastrada = None
            self.ficha_robada_actual = None
            self.casillas_destacadas = []
            self.actualizar_posiciones_fichas()
            self.actualizar_botones()
            self.verificar_y_mostrar_fin_partida()

    def procesar_motion_juego(self, evento):
        """Procesa el movimiento del mouse"""
        if hasattr(self, 'ficha_clickeada') and self.ficha_clickeada is not None and not self.partida.terminada:
            dx = evento.pos[0] - self.pos_click_x
            dy = evento.pos[1] - self.pos_click_y
            
            if (dx*dx + dy*dy) > 100:
                self.ficha_arrastrada = self.ficha_clickeada
                self.ficha_clickeada = None
                
                for pos in self.posiciones_fichas["jugador1"] + self.posiciones_fichas["jugador2"]:
                    if pos["ficha"] == self.ficha_arrastrada:
                        self.offset_x = self.pos_click_x - pos["x"]
                        self.offset_y = self.pos_click_y - pos["y"]
                        break
                
                self.actualizar_posiciones_fichas()
                self.actualizar_casillas_destacadas(self.ficha_arrastrada, self.partida.jugador_actual())
                self.mostrar_mensaje(f"📌 Arrastrando: {self.ficha_arrastrada.mostrar_valores()}")
        
        if self.ficha_arrastrada is not None and not self.partida.terminada:
            self.actualizar_casillas_destacadas(self.ficha_arrastrada, self.partida.jugador_actual())

    def procesar_soltar_ficha(self, evento):
        """Procesa cuando se suelta el mouse (colocar ficha)"""
        if evento.button != 1:
            return
        
        # Si se hizo clic para girar
        if hasattr(self, 'ficha_clickeada') and self.ficha_clickeada is not None and not self.partida.terminada:
            self.ficha_clickeada.girar_90()
            if self.sonido_girar:
                self.sonido_girar.play()
            self.offset_x = 0
            self.offset_y = 0
            self.mostrar_mensaje(f"🔄 Ficha girada: {self.ficha_clickeada.mostrar_valores()}")
            self.actualizar_posiciones_fichas()
            self.actualizar_botones()
            self.ficha_clickeada = None
            self.ficha_seleccionada = None
            return
        
        # Si hay ficha arrastrada
        if self.ficha_arrastrada is None or self.partida.terminada:
            return
        
        x, y = evento.pos
        casilla = self.obtener_casilla_en_posicion(x, y)
        
        if not casilla or casilla.ficha is not None:
            if casilla and casilla.ficha is not None:
                self.mostrar_mensaje("❌ Esa casilla ya está ocupada")
            else:
                self.mostrar_mensaje("❌ Soltar en una casilla")
            self.limpiar_estado_arrastre()
            return
        
        # Primera jugada
        if self.partida.tablero.primera_jugada:
            self.colocar_primera_ficha(casilla)
        else:
            self.colocar_ficha_normal(casilla)
        
        self.limpiar_estado_arrastre()

    def colocar_primera_ficha(self, casilla):
        """Coloca la ficha en la primera jugada"""
        if self.ficha_arrastrada.orientacion != casilla.orientacion:
            self.mostrar_mensaje(f"❌ La ficha es {self.ficha_arrastrada.orientacion} pero la casilla es {casilla.orientacion}")
            return
        
        exito = self.partida.jugar_ficha(self.ficha_arrastrada, casilla)
        if exito:
            self.mostrar_exito_colocacion()
        else:
            self.mostrar_mensaje("❌ No se pudo colocar la ficha")

    def colocar_ficha_normal(self, casilla):
        """Coloca la ficha en jugadas normales (HEAD/TAIL)"""
        head = self.partida.tablero.head_posible.casilla
        tail = self.partida.tablero.tail_posible.casilla
        
        if casilla.numero != head.numero and casilla.numero != tail.numero:
            self.mostrar_mensaje("❌ Solo se puede colocar en HEAD o TAIL")
            return
        
        if self.ficha_arrastrada.orientacion != casilla.orientacion:
            self.mostrar_mensaje(f"❌ La ficha es {self.ficha_arrastrada.orientacion} pero la casilla es {casilla.orientacion}")
            return
        
        posible, _ = self.partida.tablero.puede_colocar(self.ficha_arrastrada, casilla)
        if not posible:
            self.mostrar_mensaje("La ficha no encaja",visible=True)
            if self.sonido_error:
                self.sonido_error.play()

            # Si la nueva regla está activa, pasar turno
            if self.cambio_regla_error:
                self.partida.cambiar_turno()
                self.ficha_seleccionada = None
                self.ficha_arrastrada = None
                self.ficha_robada_actual = None
                self.casillas_destacadas = []
                self.actualizar_posiciones_fichas()
                self.actualizar_botones()
                self.verificar_y_mostrar_fin_partida()
            return
        
        exito = self.partida.jugar_ficha(self.ficha_arrastrada, casilla)
        if exito:
            self.mostrar_exito_colocacion()
        else:
            self.mostrar_mensaje("❌ No se pudo colocar la ficha")

    def mostrar_exito_colocacion(self):
        """Muestra el mensaje de éxito al colocar una ficha"""
        if self.sonido_coin:
            self.sonido_coin.play()
        
        if self.ficha_arrastrada == self.ficha_inicial and not self.ficha_inicial_colocada:
            self.ficha_inicial_colocada = True
            self.mostrar_mensaje(f"✅ {self.partida.jugador_actual().nombre} colocó la ficha inicial!")
        else:
            self.mostrar_mensaje(f"✅ {self.partida.jugador_actual().nombre} colocó {self.ficha_arrastrada.mostrar_valores()}")
        
        self.ficha_robada_actual = None
        self.actualizar_posiciones_fichas()
        self.actualizar_botones()
        self.verificar_y_mostrar_fin_partida()

    def limpiar_estado_arrastre(self):
        """Limpia el estado de arrastre"""
        self.ficha_arrastrada = None
        self.ficha_seleccionada = None
        self.casillas_destacadas = []
        self.actualizar_posiciones_fichas()
        self.actualizar_botones()
        self.ficha_clickeada = None

    def dibujar_juego(self):
        """Dibuja todos los elementos del juego"""
        self.pantalla.fill(COLOR_FONDO)
        
        self.dibujar_mensajes()
        self.dibujar_pozo()
        self.dibujar_tablero()
        self.dibujar_logo_baa()

        # Etiquetas de jugadores
        self.dibujar_etiquetas_jugadores()
        
        # Fichas de los jugadores
        self.dibujar_fichas_mano()
        
        # Botones
        for boton in self.botones:
            boton.dibujar(self.pantalla, self.fuente)
        
        # Carteles
        self.dibujar_ayuda_cartel()
        self.dibujar_confirmacion_reinicio()
        
        # Ficha arrastrada (encima de todo)
        if self.ficha_arrastrada is not None:
            x, y = pygame.mouse.get_pos()
            self.dibujar_ficha_arrastrada(
                self.ficha_arrastrada,
                x - self.offset_x,
                y - self.offset_y
            )

        # Fichas agrandadas por la lupa (encima de todo)
        if self.mostrar_lupa:
            self.dibujar_fichas_lupa()


    def dibujar_fichas_lupa(self):
        """Dibuja las fichas de los extremos (HEAD y TAIL) agrandadas."""
        factor = 2
        
        # Verificar que no haya pasado el tiempo
        if pygame.time.get_ticks() - self.tiempo_lupa >= 3000:
            self.mostrar_lupa = False
            return
        
        # Verificar que el tablero tenga fichas
        if not self.partida.tablero.fichas_jugadas:
            return
        
        # Obtener las casillas de los extremos reales de la cadena
        # head_posible apunta a la PRÓXIMA casilla libre → la ficha HEAD está en la ANTERIOR
        # tail_posible apunta a la PRÓXIMA casilla libre → la ficha TAIL está en la SIGUIENTE
        CANT_CASILLAS = len(self.partida.tablero.casillas)
        
        casilla_head = self.partida.tablero.casillas[
            (self.partida.tablero.head_posible.casilla.numero - 1) % CANT_CASILLAS
        ]
        casilla_tail = self.partida.tablero.casillas[
            (self.partida.tablero.tail_posible.casilla.numero + 1) % CANT_CASILLAS
        ]
        
        for casilla in [casilla_head, casilla_tail]:
            if casilla is None or casilla.ficha is None:
                continue
            
            ficha = casilla.ficha
            
            # Calcular dimensiones agrandadas
            if casilla.orientacion == "horizontal":
                ancho_base = self.largo_ficha
                alto_base = self.ancho_ficha
            else:
                ancho_base = self.ancho_ficha
                alto_base = self.largo_ficha
            
            ancho = int(ancho_base * factor)
            alto = int(alto_base * factor)
            
            # Posición original de la casilla
            x_base = int(casilla.x * self.escala) + self.offset_tablero_x
            y_base = int(casilla.y * self.escala) + self.offset_tablero_y
            
            # Centrar la ficha agrandada en la posición original
            x = x_base + (ancho_base - ancho) // 2
            y = y_base + (alto_base - alto) // 2
            
            # Dibujar la ficha agrandada
            if self.img_frente is not None:
                if casilla.orientacion == "vertical":
                    img = pygame.transform.smoothscale(self.img_frente_v_original, (ancho, alto))
                else:
                    img = pygame.transform.smoothscale(self.img_frente_original, (ancho, alto))
                
                self.pantalla.blit(img, (x, y))
                
                # Borde para destacarla
                pygame.draw.rect(self.pantalla, (255, 200, 50), (x, y, ancho, alto), 
                               max(2, int(4 * self.escala)), border_radius=5)
                
                self.dibujar_valores_ficha(ficha, x, y, ancho, alto, factor=factor)

    '''
    def dibujar_fichas_lupa(self):
        """Dibuja las fichas de los extremos (HEAD y TAIL) agrandadas."""
        factor = 1.8
        
        # Verificar que no haya pasado el tiempo
        if pygame.time.get_ticks() - self.tiempo_lupa >= 3000:
            self.mostrar_lupa = False
            return
        
        # Verificar que el tablero tenga fichas
        if not self.partida.tablero.fichas_jugadas:
            return
        
        # Obtener la primera y la última ficha jugada
        primera_ficha, primera_casilla = self.partida.tablero.fichas_jugadas[0]
        ultima_ficha, ultima_casilla = self.partida.tablero.fichas_jugadas[-1]
        
        for ficha, casilla in [(primera_ficha, primera_casilla), (ultima_ficha, ultima_casilla)]:
            # Calcular dimensiones agrandadas
            if casilla.orientacion == "horizontal":
                ancho_base = self.largo_ficha
                alto_base = self.ancho_ficha
            else:
                ancho_base = self.ancho_ficha
                alto_base = self.largo_ficha
            
            ancho = int(ancho_base * factor)
            alto = int(alto_base * factor)
            
            # Posición original de la casilla
            x_base = int(casilla.x * self.escala) + self.offset_tablero_x
            y_base = int(casilla.y * self.escala) + self.offset_tablero_y
            
            # Centrar la ficha agrandada en la posición original
            x = x_base + (ancho_base - ancho) // 2
            y = y_base + (alto_base - alto) // 2
            
            # Dibujar la ficha agrandada
            if self.img_frente is not None:
                if casilla.orientacion == "vertical":
                    img = pygame.transform.scale(self.img_frente_v, (ancho, alto))
                else:
                    img = pygame.transform.scale(self.img_frente, (ancho, alto))
                
                self.pantalla.blit(img, (x, y))
                
                # Borde para destacarla
                pygame.draw.rect(self.pantalla, (255, 200, 50), (x, y, ancho, alto), 
                               max(2, int(4 * self.escala)), border_radius=5)
                
                self.dibujar_valores_ficha(ficha, x, y, ancho, alto)
    '''

    def dibujar_etiquetas_jugadores(self):
        """Dibuja las etiquetas de los jugadores"""
        texto_j1 = self.fuente.render(self.nombre_jugador1, True, COLOR_JUGADOR1)
        x_j1 = int(30 * self.escala)
        y_j1 = int(50 * self.escala)
        self.pantalla.blit(texto_j1, (x_j1, y_j1))
        
        texto_j2 = self.fuente.render(self.nombre_jugador2, True, COLOR_JUGADOR2)
        x_j2 = self.ancho_pantalla - int(30 * self.escala) - texto_j2.get_width()
        y_j2 = int(50 * self.escala)
        self.pantalla.blit(texto_j2, (x_j2, y_j2))

    def dibujar_fichas_mano(self):
        """Dibuja las fichas de los jugadores"""
        jugador_actual = self.partida.jugador_actual()
        
        for jugador_id, posiciones in self.posiciones_fichas.items():
            if jugador_id == "jugador1":
                jugador = self.partida.jugadores[0]
                es_turno = (jugador_actual == jugador)
            else:
                jugador = self.partida.jugadores[1]
                es_turno = (jugador_actual == jugador)
            
            for pos in posiciones:
                es_seleccionada = pos["ficha"] == self.ficha_seleccionada and pos["ficha"] != self.ficha_arrastrada
                self.dibujar_ficha_mano(
                    pos["ficha"],
                    pos["x"], pos["y"],
                    seleccionada=es_seleccionada,
                    jugador=jugador,
                    es_turno=es_turno
                )



async def main():
    juego = JuegoPygame()
    await juego.ejecutar()

if __name__ == "__main__":
    asyncio.run(main())