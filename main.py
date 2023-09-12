
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.core.window import Window
import serial
import requests
import threading

packNumber = 0x46
nuevo_valor = -1

class MyApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)  # Blanco
        layout = GridLayout(cols=10, rows=7, size=(610, 1080))
        for i in range(1, 71):
            btn = Button(text=str(i), size_hint=(None, None), size=(87, 108), background_color=[0, 0, 0.5, 1], font_name='Roboto', font_size=14)
            btn.bind(on_press=self.on_button_press)
            layout.add_widget(btn)
        return layout

    def on_button_press(self, instance):
        global nuevo_valor
        x = instance.text
        x = int(x)
        x_he= hex(x)
        x_hex = int(x_he,16)
        nuevo_valor = x

def sendMessage():
    global nuevo_valor
    global packNumber
    try:
        ser = serial.Serial()

        ser.baudrate = 57600

        ser.port = "COM3"

        ser.stopbits = serial.STOPBITS_ONE

        ser.bytesize = serial.EIGHTBITS

        ser.open()
        
        hexWFA = 0xfa
        hexWFB = 0xfb
        hexW31 = 0x31
        hexW01 = 0x01
        hexW30 = 0x30

        #hexWFA = 0xfa
        #hexWFB = 0xfb
        #hexW42 = 0x42
        #hexW00 = 0x00
        #hexW43 = 0x43
    ##    trama = "fa-fb-03-03-"+hex(packNumber)+"-00"
        ACK = [0xfa,0xfb,0x42,0x00,0x43]
        SYNC = [0xfa,0xfb,0x31,0x01,0x31]
        #ComandoDispensar = [0xfa,0xfb,0x03,0x03,packNumber,0x00]   
        breakFlag = True
        xorStopCheck = 0xFA
        flagHexFA = False
        SubirUbi = False
        while(breakFlag):
            ComandoDispensar = [0xfa,0xfb,0x03,0x03,packNumber,0x00]
            #buffer = []
            print(nuevo_valor)
            s = ser.read()
            int_val = int.from_bytes(s,"big")
            hexByte = hex(ord(s))
            buffer = hexByte+" "
            print(hexByte," ",int_val)
            if(int_val == 0xfa):
                flagHexFA = True
                while(flagHexFA == True):
                    s = ser.read()
                    int_val = int.from_bytes(s,"big")
                    hexByte = hex(ord(s))
                    buffer += hexByte+" "
                    if(xorStopCheck == int_val):
                        flagHexFA = False
                        xorStopCheck = 0xfa
                        if(nuevo_valor == -1):
                            print(buffer)
                            bufferSplit = buffer.split(" ")
                            command = int(bufferSplit[2],16)
                            #vmcPackCount = int(bufferSplit[4],16)
                            
                            if(command == 0x31):
                                for byte in SYNC:
                                    print(hex(byte))
                                    ser.write(byte.to_bytes(1,'big'))
                                #registerLastDispensed(str(int(buffer[7],16)))
                            elif(command == 0x04):
                                
                                checkSuccess = int(bufferSplit[5],16)
                                if(checkSuccess == 0x11):
                                    cellNumber = int(bufferSplit[7],16)
                                if(checkSuccess == 0x02):
                                    SubirUbi = True
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("-------------------SUCCESS-------------------")
                                    print(cellNumber)
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                    print("---------------------------------------------")
                                if(checkSuccess == 0x24):
                                    if SubirUbi:
                                        
                                        registerLastDispensed(str(cellNumber))
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("-------------------UBIDOTS-------------------")
                                        print(cellNumber)
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")
                                        print("---------------------------------------------")

                                        SubirUbi = False
                                        
                                for byte in ACK:
                                    print(hex(byte))
                                    ser.write(byte.to_bytes(1,'big'))
                            elif(command == 0x11):
                                print("---------------------------------------------")
                                print("---------------------------------------------")
                                print("---------------------------------------------")
                                print(packNumber)
                                print("---------------------------------------------")
                                print("---------------------------------------------")
                                print("---------------------------------------------")
                                if(command != 0x42):
                                    for byte in ACK:
                                        print(hex(byte))
                                        ser.write(byte.to_bytes(1,'big'))
                            else:
                                for byte in ACK:
                                    print(hex(byte))
                                    ser.write(byte.to_bytes(1,'big'))
                        else:
                            print(buffer)
                            bufferSplit = buffer.split(" ")
                            command = int(bufferSplit[2],16)
    ##                        command = int(buffer[2],16)
    ##                        if(command == 0x31):
    ##                            for byte in SYNC:
    ##                                print(hex(byte))
    ##                                ser.write(byte.to_bytes(1,'big'))
    ##                        else:
    ##                            for byte in ACK:
    ##                                print(hex(byte))
    ##                                ser.write(byte.to_bytes(1,'big'))
    ##                        print(nuevo_valor)
                            ComandoDispensar.append(nuevo_valor)
                            resultado = ComandoDispensar[0]
            
                            for numero in ComandoDispensar[1:]:
                                resultado ^= numero
                            ComandoDispensar.append(resultado)
                            print("---------------------------------------------")
                            print("---------------------------------------------")
                            print("---------------------------------------------")
                        
                            for i in ComandoDispensar:
                                
                                    print(hex(i))
                                    ser.write(i.to_bytes(1,'big'))
                            print("---------------------------------------------")
                            print("---------------------------------------------")
                            print("---------------------------------------------")
                            packNumber += 1
                            nuevo_valor = -1
                            
                            
                    else:
                        xorStopCheck ^= int_val
    except Exception as e:
        print(f"error:{e}")


def sendACK():
    pass

def registerLastDispensed(cellNO):
    apiToken = "BBFF-03ETGJsi5qDM6Tfqtol7HnI9sSEWcU"
    apiLastDispensedV = "ultimo_dispensado"
    apiURL = "http://industrial.api.ubidots.com/api/v1.6/devices/VMS"
    headers = {"Content-Type":"application/json",
            "X-Auth-Token":apiToken}
    data = {apiLastDispensedV:cellNO}
    try:
        r = requests.post(url=apiURL,headers = headers, json=data, verify = False)
    except Exception as e:
        print(e)

        
vmcThread = threading.Thread(target = sendMessage)
vmcThread.start()

while True:
    MyApp().run()
