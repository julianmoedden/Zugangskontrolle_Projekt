################################
###Zugangskontrolle_Projekt
###Julian Mödden
###erstellt:18.03.2025
###zuletzt bearbeitet:18.03.2025
################################

#----------------Bibliotheken------------------#

from machine import Pin, SPI, SoftI2C	#Hardwareanschlüsse
import time, network, socket			#Zeit zum sleep, WLan und Port
from ahtx0 import AHT10					#AHT10 Temperatur/Luft
import st7789py as st7789
import vga1_16x32 as font

#----------------Sensor AHT10------------------#

i2ct = SoftI2C(scl=Pin(5), sda=Pin(4))	#I2C für AHT10

sensort = AHT10(i2ct)					#Sensorobjekt erstellen

#---------------Display st7789-----------------#

#Initialisierung des SPI
spi = SPI(1,
          baudrate = 20000000,
          polarity = 0,
          phase = 0,
          sck = Pin(39),
          mosi = Pin(40),
          miso = Pin(0))

#Initialisierung des Displays
display = st7789.ST7789(
    spi,
    240,
    320,
    reset = Pin(41, Pin.OUT),
    cs = Pin(2, Pin.OUT),
    dc = Pin(42, Pin.OUT),
    backlight = Pin(0, Pin.OUT),
    rotation = 3)

#--------------Daten auswerten-----------------#

while True:
    
#Display löschen
    #display.fill(st7789.BLACK)
    
#Auswertung der Sensorwerte
    try:
        Temp = round(sensort.temperature,0)
    except:
        Temp = "undefined"						#Bei Ausfall eines Sensors, läuft das Programm weiter
        
    try:
        Luft = round(sensort.relative_humidity,0)
    except:
        Luft = "undefined"
        
    #Textanzeige
    display.text(font, "Temp = {} C".format(Temp), 30, 30, st7789.WHITE, st7789.BLACK)
    display.text(font, "Luft = {} %".format(Luft), 30, 50, st7789.WHITE, st7789.BLACK)
        
    print(Temp, ", ", Luft)
        
    time.sleep(2)