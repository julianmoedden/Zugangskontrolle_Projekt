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

#----------------Sensor AHT10------------------#

i2ct = SoftI2C(scl=Pin(42), sda=Pin(2))	#I2C für AHT10

sensort = AHT10(i2ct)					#Sensorobjekt erstellen

#--------------Daten auswerten-----------------#

while True:
#Auswertung der Sensorwerte
    try:
        Temp = round(sensort.temperature,0)
    except:
        Temp = "undefined"						#Bei Ausfall eines Sensors, läuft das Programm weiter
        
    try:
        Luft = round(sensort.relative_humidity,0)
    except:
        Luft = "undefined"
        
    print(Temp, ", ", Luft)
        
    time.sleep(2)