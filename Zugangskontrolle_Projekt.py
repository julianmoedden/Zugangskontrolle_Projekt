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
from mfrc522 import MFRC522
from machine import Pin, SPI, SoftSPI#Hardwareanschlüsse


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

#--------------Chiperkennung-----------------#

sck = Pin(17, Pin.OUT)
copi = Pin(16, Pin.OUT) # Controller out, peripheral in
cipo = Pin(15, Pin.OUT) # Controller in, peripheral out
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=copi, miso=cipo)
sda = Pin(18, Pin.OUT)
reader = MFRC522(spi, sda)

#--------------Hauptprogramm-----------------#

Startzeit = time.ticks_ms()
#Auswertung der Sensorwerte
while True:
    
    if time.ticks_diff(time.ticks_ms(), Startzeit) >= 2000:
        Startzeit = time.ticks_ms()
    
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
        display.text(font, "{} C".format(Temp), 20, 30, st7789.WHITE, st7789.BLACK)
        display.text(font, "{} %".format(Luft), 200, 30, st7789.WHITE, st7789.BLACK)
            
        print(Temp, ", ", Luft)
    
    else:
        try:
            (status, tag_type) = reader.request(reader.CARD_REQIDL)
            if status == reader.OK:
                (status, raw_uid) = reader.anticoll()
                if status == reader.OK:
                    print (' uid: 0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                    
                    if '0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]) == "0x3cd6ef31":
                        display.text(font, "Willkommen".format(Temp), 80, 90, st7789.WHITE, st7789.BLACK)
                        display.text(font, "Julian Moedden".format(Temp), 40, 130, st7789.WHITE, st7789.BLACK)
                    
                    else:
                        display.text(font, "Zugang".format(Temp), 100, 90, st7789.WHITE, st7789.BLACK)
                        display.text(font, "verweigert".format(Temp), 70, 130, st7789.WHITE, st7789.BLACK)
                
                else:
                    print ("Tag nicht erkannt")
        except KeyboardInterrupt:
            break