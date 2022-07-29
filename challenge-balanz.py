from decimal import DivisionByZero
import msvcrt
import asyncio
from time import sleep
from unicodedata import name
import requests
import websockets
import sys, os
import json

url_list_security_id = "https://test-algobalanz.herokuapp.com/api/v1/prices/security_id"
url_list_instant_prices = "https://test-algobalanz.herokuapp.com/api/v1/prices"
url_security_id_detail = "https://test-algobalanz.herokuapp.com/api/v1/prices/security_id/"
url_websocket_service = 'wss://test-algobalanz.herokuapp.com/ws/generic'

instruments = []
instrument_base_names= []

class Instrument:
    
    def __init__ (self, name ):
        self.name=name
        self.price=""
        self.currency=""
        self.setlement_type=""
        self.dollar_cable=""
        self.dollar_mep=""

    def __str__(self) -> str:
        return (self.name + '\t' + str(self.price) + '\t' + self.currency + '\t' + self.setlement_type + "\t"+ str(self.dollar_cable) + "\t"+ str(self.dollar_mep) )


def init_instruments():
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
    
    try:
        req_instant_price_ids = requests.get(url_list_instant_prices)
        req_instant_price_ids_json =  json.loads(req_instant_price_ids.text)

        for instrument in instruments:
            # Por si no esta en la respuesta
            try:
                instrument_detail =req_instant_price_ids_json[instrument.name]
                instrument.price = instrument_detail['last']['price']
                instrument.setlement_type = instrument_detail["settlementType"]
                instrument.currency = instrument_detail["currency"]

            except Exception as e:
                print(e)

    except Exception as e:
        print (e)

def print_console():
    for instrument in instruments:
        print(instrument)

def init():
    init_instruments()
    initial_price_instruments()

# Consumo wss


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
                    instrument.dollar_cable = instrument_base.price / float(instrument.price)
                except DivisionByZero as e:
                    print ('division por 0 en cable')
                    print("instrument del error: " +instrument)
                    pass
            else:
                try:
                    instrument.dollar_mep = instrument_base.price / float(instrument.price)
                except DivisionByZero as e:
                    print ('division por 0 en mep')
                    print("instrument del error: " +instrument.name)
                    pass



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
                print(msg)
                parser_broadcast_msg(msg)
                calculate_dollar()
                print_console()
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




def main():
    init()
    print_console()
    active_wss()


main()


msvcrt.getch()