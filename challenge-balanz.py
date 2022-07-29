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

Instruments = []

class Instrument:
    
    def __init__ (self, name ):
        self.name=name
        self.price=""
        self.currency=""
        self.setlement_type=""

    def __str__(self) -> str:
        return (self.name + ' ' + str(self.price) + ' ' + self.currency + ' ' + self.setlement_type)

def init_instruments():
    try:
        req_security_ids = requests.get(url_list_security_id)
        req_security_ids_json = json.loads(req_security_ids.text)
        list_security_id = list(req_security_ids_json["response"])

        for instrumento_name in list_security_id:
            instrument = Instrument(instrumento_name)       
            Instruments.append(instrument)

    except Exception as e:
        print (e)

def initial_price_instruments():
    
    try:
        req_instant_price_ids = requests.get(url_list_instant_prices)
        req_instant_price_ids_json =  json.loads(req_instant_price_ids.text)

        for instrument in Instruments:
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


def init():
    init_instruments()
    initial_price_instruments()

init()













# Consumo wss
# async def wss():
#     async with websockets.connect(url_websocket_service) as websocket:
#         while True:
#             try:
#                 recv = await websocket.recv()
#                 msg = json.loads(recv)["msg"]
#                 print(msg, end='\r')
#                 sleep(1)
                
#             except Exception as e:
#                 print (e)


# loop = asyncio.get_event_loop()
# try: 
#     loop.create_task(wss())
#     loop.run_forever()
# except Exception as e:
#     print (e)
# finally:
#     loop.close()


msvcrt.getch()