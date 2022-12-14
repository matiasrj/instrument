from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal, DivisionByZero
import msvcrt
import asyncio
from time import sleep
from unicodedata import name
import requests
import websockets
import sys, os
import json

# Enviro info
url_list_security_id = "https://test-algobalanz.herokuapp.com/api/v1/prices/security_id"
url_list_instant_prices = "https://test-algobalanz.herokuapp.com/api/v1/prices"
url_security_id_detail = "https://test-algobalanz.herokuapp.com/api/v1/prices/security_id/"
url_websocket_service = 'wss://test-algobalanz.herokuapp.com/ws/generic'

# Initial variables
instruments = []
instrument_base_names= []

class Instrument:
    
    def __init__ (self, name ):
        self.name=name
        self.price=""
        self.currency=""
        self.setlement_type=""
        self.dollar_cable="0"
        self.dollar_mep="0"

    def __str__(self) -> str:

        self.price = Decimal(self.price).quantize(Decimal('.0001'),ROUND_HALF_UP)
        self.dollar_cable = Decimal(self.dollar_cable).quantize(Decimal('.0001'),ROUND_HALF_UP)
        self.dollar_mep = Decimal(self.dollar_mep).quantize(Decimal('.0001'),ROUND_HALF_UP)  
        return (self.name + '\t - \t' + 
                f'{str(self.price):10}' + '\t - \t' +
                self.currency + '\t - \t' + 
                self.setlement_type + "\t - \t"+  
                f'{str(self.dollar_cable):10}' + '\t - \t' +
                str(self.dollar_mep)
                 )

#####################################
# initialization functions
#####################################

def init_instruments():
    # Creation of instruments
    try:
        req_security_ids = requests.get(url_list_security_id)
        req_security_ids_json = json.loads(req_security_ids.text)
        list_security_id = list(req_security_ids_json["response"])

        for instrumento_name in list_security_id:
            instrument = Instrument(instrumento_name)       
            instruments.append(instrument)
    except Exception as e:
        print (e)

def initial_price_instruments():
    # First Survey of instruments_data
    try:
        req_instant_price_ids = requests.get(url_list_instant_prices)
        req_instant_price_ids_json =  json.loads(req_instant_price_ids.text)

        for instrument in instruments:
            # Por si no esta en la respuesta
            try:
                instrument_detail =req_instant_price_ids_json[instrument.name]
                instrument.price = Decimal(instrument_detail['last']['price'])
                instrument.setlement_type = instrument_detail["settlementType"]
                instrument.currency = instrument_detail["currency"]

            except Exception as e:
                print(e)

    except Exception as e:
        print (e)


# initialization
def init():
    init_instruments()
    initial_price_instruments()





#####################################
# Consumo wss functions
#####################################


def buscar_instrument_base ( instrument_ref ):
    name = instrument_ref.name
    name_splited = name.split("-")

    if instrument_ref.currency == "USD":
        name_splited[0] =  name_splited[0][:-1]
    else:
        name_splited[0] =  name_splited[0][:-1]

    name_splited.pop()
    name_splited.append("ARS")
    glue = '-'
    name = glue.join(name_splited)
    for instrument in instruments:
        if instrument.name == name:
            return instrument

def calculate_dollar():
    # Calculo, segun tipo de instrumento
    for instrument in instruments:
        if instrument.currency in ["USD", "EXT"]:
            instrument_base = buscar_instrument_base(instrument)
            
            if instrument.currency == "USD":
                try:
                    instrument.dollar_cable = Decimal(instrument_base.price) / Decimal(instrument.price)
                except Exception as e:
                    pass
            else:
                try:
                    instrument.dollar_mep = Decimal(instrument_base.price) / Decimal(instrument.price)
                except Exception as e:
                    pass

def print_console():
    print (f'{ "Name":20}' + '\t - \t' + 
           f'{ "Price":8}'+ '\t - \t' +
           f'{ "Currency"}'+ ' -   ' +
           f'{ "Setlement_type"}'+ '  - \t' +
           f'{ "Dollar_Cable":10}'+ '\t - ' +
           f'{ "Dollar_mep":10}' + '\n\n')
    

    for instrument in instruments:
        print(instrument)
        
    print("\n\n=========================================\n\n")


def parser_broadcast_msg(msg):
    pass
    securityID = msg["securityID"]
    for instrument in instruments :
        if securityID == instrument.name:
            instrument.price = msg["last"]["price"] 

async def wss():
    async with websockets.connect(url_websocket_service) as websocket:
        while True:
            try:
                recv = await websocket.recv()
                msg = json.loads(recv)["msg"]
                # print(msg)
                parser_broadcast_msg(msg)
                calculate_dollar()
                print_console()

                # Nota: No logre refrescar la console en la misma linea, por lo tanto,
                # sin sleep, se imprime en consola demasiado rapido, no permite observar 
                # ( y validar ) los calculos. 
                sleep(10)
            except Exception as e:
                print (e)

def active_wss():    
    loop = asyncio.get_event_loop()
    try: 
        loop.create_task(wss())
        loop.run_forever()
    except Exception as e:
        print (e)
    finally:
        loop.close()


#####################################
# Start APP
#####################################


def main():
    init()
    print_console()
    active_wss()


main()


msvcrt.getch()