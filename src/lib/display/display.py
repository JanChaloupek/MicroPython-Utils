# ------------------------------------------------------------
# display.py – obalovací knihovna pro displej pico:ed (MicroPython)
# Verze: 2.4
# Datum: 26. 1. 2026
#
# Hlavní vlastnosti:
#   - instanční architektura (žádné statické metody)
#   - řízený singleton: from display import display
#   - vlastní framebuffer (17×7)
#   - dirty mapa (jen změněné pixely se překreslují)
#   - postupné překreslování (2 pixely / cyklus)
#   - automatický refresh pomocí Timer-u
#   - kompatibilní API s původní CircuitPython verzí
#   - kompletní sada piktogramů
# ------------------------------------------------------------

from machine import I2C, Pin, ADC
from picoed_v2_lib.display import Display as HWDisplay
from picoed_v2_lib.iic import IIC
import _thread
import time


# ------------------------------------------------------------
# Battery – měření napětí
# ------------------------------------------------------------

class Battery:
    _adc = ADC(26)
    _VOLTAGE_SCALE = 0.000147

    def get_voltage(self):
        raw = Battery._adc.read_u16()
        return raw * Battery._VOLTAGE_SCALE


# ------------------------------------------------------------
# Display – hlavní třída
# ------------------------------------------------------------

class Display:
    WIDTH = 17
    HEIGHT = 7

    def __init__(self, auto_refresh_delay_ms=None):
        # framebuffer
        self.framebuffer = [bytearray(self.WIDTH) for _ in range(self.HEIGHT)]
        self.dirty = [[True for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]

        # kurzor pro postupné překreslování
        self.cursor_x = 0
        self.cursor_y = 0

        # I2C driver
        i2c0 = I2C(IIC.BUS0, scl=Pin(IIC.SCL0), sda=Pin(IIC.SDA0))
        # HW driver displeje (dědí z Matrix)
        self.driver = HWDisplay(i2c0)

        # auto-refresh
        self._running = False
        self.auto_start(auto_refresh_delay_ms)

    def _auto_loop(self):
        while self._running:
            self.update()
            time.sleep_ms(self._delay)

    def _start_auto_refresh(self):
        if self._running:
            return
        self._running = True
        _thread.start_new_thread(self._auto_loop, ())

    def auto_stop(self):
        self._running = False
        
    def auto_start(self, auto_refresh_delay_ms=1):
        self._delay = auto_refresh_delay_ms
        if auto_refresh_delay_ms is not None:
            self._start_auto_refresh()

    # --------------------------------------------------------
    # Základní operace
    # --------------------------------------------------------

    def clear(self):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self.framebuffer[y][x] = 0
                self.dirty[y][x] = True

    def pixel(self, x, y, brightness):
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:

            # saturace mimo rozsah
            if brightness < 0:
                brightness = 0
            elif brightness > 255:
                brightness = 255
            old = self.framebuffer[y][x]
            self.framebuffer[y][x] = brightness
            self.dirty[y][x] = (old != brightness)

    # --------------------------------------------------------
    # Postupné překreslování
    # --------------------------------------------------------

    def update(self):
        self._update_one_pixel()
        self._update_one_pixel()

    def _update_one_pixel(self):
        x = self.cursor_x
        y = self.cursor_y

        # posun kurzoru
        self.cursor_x += 1
        if self.cursor_x >= self.WIDTH:
            self.cursor_x = 0
            self.cursor_y += 1
            if self.cursor_y >= self.HEIGHT:
                self.cursor_y = 0

        # překreslení
        if self.dirty[y][x]:
            self.dirty[y][x] = False
            # mapování na Matrix driver (16×9)
            if x < 16 and y < 9:
                self.driver.pixel(x, y, self.framebuffer[y][x])

            return True

        return False

    # --------------------------------------------------------
    # Bitmapy, piktogramy, ikony
    # --------------------------------------------------------

    PICT = {
        # -----------------------------
        # ŠIPKY
        # -----------------------------
        '>':  [0b00100, 0b00010, 0b11111, 0b00010, 0b00100],
        '<':  [0b00100, 0b01000, 0b11111, 0b01000, 0b00100],
        '^':  [0b00100, 0b00100, 0b10101, 0b01110, 0b00100],
        'v':  [0b00100, 0b01110, 0b10101, 0b00100, 0b00100],

        # aliasy
        '→':  [0b00100, 0b00010, 0b11111, 0b00010, 0b00100],
        '←':  [0b00100, 0b01000, 0b11111, 0b01000, 0b00100],
        '↑':  [0b00100, 0b00100, 0b10101, 0b01110, 0b00100],
        '↓':  [0b00100, 0b01110, 0b10101, 0b00100, 0b00100],

        # -----------------------------
        # KŘIŽOVATKY
        # -----------------------------
        'TL': [0b00100, 0b00100, 0b11100, 0b00000, 0b00000],
        'TR': [0b00100, 0b00100, 0b00111, 0b00000, 0b00000],
        'IT': [0b00100, 0b00100, 0b11111, 0b00000, 0b00000],
        'IL': [0b00100, 0b00100, 0b11100, 0b00100, 0b00100],
        'IR': [0b00100, 0b00100, 0b00111, 0b00100, 0b00100],
        'I+': [0b00100, 0b00100, 0b11111, 0b00100, 0b00100],

        # -----------------------------
        # ODDĚLOVAČE
        # -----------------------------
        '--': [0b00000, 0b00000, 0b11111, 0b00000, 0b00000],
        ' -': [0b00000, 0b00000, 0b00111, 0b00000, 0b00000],
        '- ': [0b00000, 0b00000, 0b11100, 0b00000, 0b00000],

        '_':  [0b11111, 0b00000, 0b00000, 0b00000, 0b00000],
        '.':  [0b00100, 0b00000, 0b00000, 0b00000, 0b00000],
        ',':  [0b00100, 0b00010, 0b00000, 0b00000, 0b00000],
        '|':  [0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
        '/':  [0b10000, 0b01000, 0b00100, 0b00010, 0b00001],
        '\\': [0b00001, 0b00010, 0b00100, 0b01000, 0b10000],

        # -----------------------------
        # SPECIÁLNÍ SYMBOLY
        # -----------------------------
        's':  [0b11100, 0b00010, 0b01110, 0b01000, 0b00111],
        'x':  [0b10001, 0b01010, 0b00100, 0b01010, 0b10001],
        ' ':  [0b00000]*5,

        # -----------------------------
        # ČÍSLA 0–9
        # -----------------------------
        '0':  [0b01110, 0b01010, 0b01010, 0b01010, 0b01110],
        '1':  [0b00100, 0b00100, 0b00100, 0b01100, 0b00100],
        '2':  [0b01110, 0b01000, 0b01110, 0b00010, 0b01110],
        '3':  [0b01110, 0b00010, 0b00110, 0b00010, 0b01110],
        '4':  [0b00010, 0b00010, 0b01110, 0b01010, 0b01010],
        '5':  [0b01110, 0b00010, 0b01110, 0b01000, 0b01110],
        '6':  [0b01110, 0b01010, 0b01110, 0b01000, 0b01110],
        '7':  [0b00010, 0b00010, 0b00010, 0b00010, 0b01110],
        '8':  [0b01110, 0b01010, 0b01110, 0b01010, 0b01110],
        '9':  [0b01110, 0b00010, 0b01110, 0b01010, 0b01110],

        # -----------------------------
        # PÍSMENA A–Z
        # -----------------------------
        'A': [0b01010, 0b01010, 0b01110, 0b01010, 0b00100],
        'B': [0b01100, 0b01010, 0b01100, 0b01010, 0b01100],
        'C': [0b00110, 0b01000, 0b01000, 0b01000, 0b00110],
        'D': [0b01100, 0b01010, 0b01010, 0b01010, 0b01100],
        'E': [0b01110, 0b01000, 0b01100, 0b01000, 0b01110],
        'F': [0b01000, 0b01000, 0b01100, 0b01000, 0b01110],
        'G': [0b00110, 0b01010, 0b01000, 0b01000, 0b00110],
        'H': [0b01010, 0b01010, 0b01110, 0b01010, 0b01010],
        'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b01110],
        'J': [0b00100, 0b01010, 0b00010, 0b00010, 0b00010],
        'K': [0b01010, 0b01100, 0b01000, 0b01100, 0b01010],
        'L': [0b01110, 0b01000, 0b01000, 0b01000, 0b01000],
        'M': [0b01010, 0b01010, 0b01110, 0b01110, 0b01010],
        'N': [0b01010, 0b01110, 0b01110, 0b01010, 0b01010],
        'O': [0b00100, 0b01010, 0b01010, 0b01010, 0b00100],
        'P': [0b01000, 0b01000, 0b01100, 0b01010, 0b01100],
        'Q': [0b00110, 0b01110, 0b01010, 0b01010, 0b00100],
        'R': [0b01010, 0b01100, 0b01100, 0b01010, 0b01100],
        'S': [0b01100, 0b00010, 0b00100, 0b01000, 0b00110],
        'T': [0b00100, 0b00100, 0b00100, 0b00100, 0b11111],
        'U': [0b00100, 0b01010, 0b01010, 0b01010, 0b01010],
        'V': [0b00100, 0b01010, 0b01010, 0b01010, 0b01010],
        'W': [0b01010, 0b01110, 0b01010, 0b01010, 0b01010],
        'X': [0b01010, 0b01010, 0b00100, 0b01010, 0b01010],
        'Y': [0b00100, 0b00100, 0b00100, 0b01010, 0b01010],
        'Z': [0b01110, 0b01000, 0b00100, 0b00010, 0b01110],

        # -----------------------------
        # ROZŠÍŘENÉ IKONY
        # -----------------------------
        'heart':  [0b01010, 0b11111, 0b11111, 0b01110, 0b00100],
        'smile':  [0b00000, 0b01010, 0b00000, 0b10001, 0b01110],
        'sad':    [0b00000, 0b01010, 0b00000, 0b01110, 0b10001],
        'wifi':   [0b00100, 0b01010, 0b10001, 0b00000, 0b00100],
        'load1':  [0b00100, 0b00000, 0b00000, 0b00000, 0b00000],
        'load2':  [0b00100, 0b00100, 0b00000, 0b00000, 0b00000],
        'load3':  [0b00100, 0b00100, 0b00100, 0b00000, 0b00000],
        'load4':  [0b00100, 0b00100, 0b00100, 0b00100, 0b00000],
        'load5':  [0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
        'battery': [0b11111, 0b10001, 0b10001, 0b10001, 0b11111],
    }

    def _bitmap(self, x, y, width, lines):
        for iy, line in enumerate(lines):
            for ix in range(width):
                bit = (line >> ix) & 1
                self.pixel(x + ix, y + iy, 3 if bit else 0)

    def _iconA(self, ch):
        self._bitmap(12, 0, 5, self.PICT[ch])

    def _iconB(self, ch):
        self._bitmap(6, 0, 5, self.PICT[ch])

    def _iconC(self, ch):
        self._bitmap(0, 0, 5, self.PICT[ch])

    # --------------------------------------------------------
    # Vyšší funkce
    # --------------------------------------------------------

    def number(self, num):
        s = "{:3d}".format(num)
        self._iconA(s[0])
        self._iconB(s[1])
        self._iconC(s[2])

    def drive_mode(self, mode):
        self._iconB(mode)

    def position(self, x, y):
        self._iconA(str(min(9, int(x))))
        self._iconC(str(min(9, int(y))))

    def positionEmpty(self):
        self._iconA(" ")
        self._iconC(" ")

    def sensors(self, obstacleLeft, farLeft, left,
                middleLeft, middle35, middleRight,
                right, farRight, obstacleRight,
                bh, bl):

        # levá strana
        self.pixel(16, 6, bh if obstacleLeft else bl)
        if farLeft is not None:
            self.pixel(13, 6, bh if farLeft else bl)
        self.pixel(11, 6, bh if left else bl)

        # pravá strana
        if farRight is not None:
            self.pixel(3, 6, bh if farRight else bl)
        if middleLeft is not None:
            self.pixel(9, 6, bh if middleLeft else bl)
        if middle35 is not None:
            self.pixel(8, 6, bh if middle35 else bl)
        self.pixel(5, 6, bh if right else bl)
        if middleRight is not None:
            self.pixel(7, 6, bh if middleRight else bl)
        self.pixel(0, 6, bh if obstacleRight else bl)


# ------------------------------------------------------------
# ŘÍZENÝ SINGLETON
# ------------------------------------------------------------

display = Display()
battery = Battery()
