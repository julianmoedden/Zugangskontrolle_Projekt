################################
###Zugangskontrolle_Projekt
###Julian Mödden
###erstellt:18.03.2025
###zuletzt bearbeitet:18.03.2025
################################

#----------------Bibliotheken------------------#

from machine import Pin, SPI, SoftI2C, PWM	#Hardwareanschlüsse
import time, network, socket, json				#Zeit zum sleep, WLan und Port
from umqtt.simple import MQTTClient			#MQTT zum Empfangen der Daten
from ahtx0 import AHT10						#AHT10 Temperatur/Luft
import st7789py as st7789					#Display zum Anzeigen
import vga1_16x32 as font					#Anzeigeeinstellung
from mfrc522 import MFRC522					#Chiperkennung
from machine import Pin, SPI, SoftSPI		#Hardwareanschlüsse

#---------------- Funktion zur Datenauswertung ------------- 
def sub_button(topic, msg):  
    daten = json.loads(msg) 
    button = daten.get('manual') 
    if button == "OPEN":     
# Knopf ist gedrückt 
        global door_open    
#neue Variable erzeugen 
        door_open = True
        print(button)
    else: 
        global door_open 
        door_open = False     # Wichtig: Globale Variable nutzen und keine 
        print(button)
        # sonst ausschalten 

#-------Initialisieren der WLan-Verbindung---------#

#WLan Anmeldedaten
ssid = "BZTG-IoT"
passwort = "WerderBremen24"

wlan = network.WLAN(network.STA_IF)		#WLan-Client erzeugen
wlan.active(False)						#WLan reset (zum Trennen aller Verbindungen)
wlan.active(True)						#WLan einschalten
time.sleep(0.5)								#warten bis WLan eingeschaltet ist
wlan.connect(ssid,passwort)				#Verbindung zum WLan herstellen

while not wlan.isconnected():			#warten bis WLan verbunden ist
    print("Verbindung wird hergestellt...")
    time.sleep(0.5)
    pass

print("""Verbunden.
IP-Adresse: """, wlan.ifconfig()[0])	#Textausgabe mit Verbindungsdaten

#------------------------MQTT-----------------------#

BROKER = "192.168.1.218"						#MQTT-Broker (mosquitto)
PORT = 1883										#Portnummer
CLIENT_ID = "JMD"								#client ID
TOPIC_C = "esp32/sensor"						#Das Topic Chiperkennung
TOPIC_S = "esp32/umw"							#das Topic Umweltdaten
TOPIC_M = "esp32/manual"						#das abonnierte Topic Tür manuell öffnen

client = MQTTClient(CLIENT_ID, BROKER, PORT)	#Client Einstellungen
#Verbindung mit Client
client.set_callback(sub_button)
time.sleep(1)
client.connect()
client.subscribe(TOPIC_M)
print("Mit MQTT-BROKER verbinden")

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

#--------------Servo-Motor-------------------#

pwm_pin_servo = PWM(Pin(38))	#Pin für Servo
pwm_pin_servo.freq(50)			#Bestimmen der Frequenz

#Berechnung Servobereich
def set_servo_angle(angle):
    
    duty_servo = int(min_duty + (angle / 180) * (max_duty - min_duty))
    pwm_pin_servo.duty_u16(duty_servo)
    
#duty_Bereich
min_duty = 1000
max_duty = 9000

#Berechnung Servobereich
def set_servo_angle(angle):
    
    duty_servo = int(min_duty + (angle / 180) * (max_duty - min_duty))
    pwm_pin_servo.duty_u16(duty_servo)

#--------------Hauptprogramm-----------------#

Startzeit = time.ticks_ms()
#Auswertung der Sensorwerte
while True:
    set_servo_angle(220)
    
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
        display.text(font, "Bitte die Karte".format(Temp), 40, 90, st7789.WHITE, st7789.BLACK)
        display.text(font, "vorhalten.".format(Temp), 80, 130, st7789.WHITE, st7789.BLACK)
        
        #Werte als JSON-Datei erstellen
        werte = {"Temperatur": Temp,
                 "Luftfeuchtigkeit": Luft}

        json_string = json.dumps(werte)

    #Nachricht senden
        client.publish(TOPIC_S, json_string)
        print(f"Nachricht gesendet: {json_string}")
    
    elif client.check_msg():
        print (door_open)
        if door_open:
            display.fill(st7789.BLACK)
            display.text(font, "Willkommen".format(Temp), 80, 90, st7789.WHITE, st7789.BLACK)
            set_servo_angle(40)
            #Werte als JSON-Datei erstellen
            zugang = {"Zugang": "Manuell"}

            json_zugang = json.dumps(zugang)

            #Nachricht senden
            client.publish(TOPIC_C, json_zugang)
            print(f"Nachricht gesendet: {json_zugang}")
            time.sleep(10)
            display.fill(st7789.BLACK)
        else:
            continue
    else:
        try:
            (status, tag_type) = reader.request(reader.CARD_REQIDL)
            if status == reader.OK:
                (status, raw_uid) = reader.anticoll()
                if status == reader.OK:
                    print (' uid: 0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                    
                    if '0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]) == "0x3cd6ef31":
                        display.fill(st7789.BLACK)
                        display.text(font, "Willkommen".format(Temp), 80, 90, st7789.WHITE, st7789.BLACK)
                        display.text(font, "Julian Moedden".format(Temp), 40, 130, st7789.WHITE, st7789.BLACK)
                        set_servo_angle(40)
                        #Werte als JSON-Datei erstellen
                        zugang = {"Zugang": "Julian Moedden"}

                        json_zugang = json.dumps(zugang)

                        #Nachricht senden
                        client.publish(TOPIC_C, json_zugang)
                        print(f"Nachricht gesendet: {json_zugang}")
                        time.sleep(10)
                        display.fill(st7789.BLACK)
                        
                    elif '0x%02x%02x%02x%02x' % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]) == "0x6ce81732":
                        display.fill(st7789.BLACK)
                        display.text(font, "Willkommen".format(Temp), 80, 90, st7789.WHITE, st7789.BLACK)
                        display.text(font, "Jan-Luca Benkens".format(Temp), 30, 130, st7789.WHITE, st7789.BLACK)
                        set_servo_angle(40)
                        #Werte als JSON-Datei erstellen
                        zugang = {"Zugang": "Jan-Luca Benkens"}

                        json_zugang = json.dumps(zugang)

                        #Nachricht senden
                        client.publish(TOPIC_C, json_zugang)
                        print(f"Nachricht gesendet: {json_zugang}")
                        time.sleep(10)
                        display.fill(st7789.BLACK)
                    
                    else:
                        display.fill(st7789.BLACK)
                        display.text(font, "Zugang".format(Temp), 100, 90, st7789.WHITE, st7789.BLACK)
                        display.text(font, "verweigert".format(Temp), 70, 130, st7789.WHITE, st7789.BLACK)
                        #Werte als JSON-Datei erstellen
                        zugang = {"Zugang": "fehlerhafter Zugang"}

                        json_zugang = json.dumps(zugang)

                        #Nachricht senden
                        client.publish(TOPIC_C, json_zugang)
                        print(f"Nachricht gesendet: {json_zugang}")
                        time.sleep(2)
                        display.fill(st7789.BLACK) 
                
                else:
                    print ("Tag nicht erkannt")
        except KeyboardInterrupt:
            display.fill(st7789.BLACK)
            set_servo_angle(220)
            break