#!/usr/bin/python3           # This is client.py file

#Collect spectral data to be passed to a web client via Node Server
#Recuperation des données  spectre de GNU_Radio et envoi vers le client web
import socket
import asyncio
import time
import websockets
import numpy as np

# get local machine name
host = 'localhost'                           


port_spectre_web = 8002
port_spectre_GR = 19002
Connected_to_GR = False
byte_array = bytearray(65536) #16*4096
packet_number=0
nb_erreur=0

     

async def read_maia_Spectre():
    global byte_array, packet_number, nb_erreur, Connected_to_GR
    uri = f"ws://127.0.0.1:8000/waterfall"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("Connected to GR spectre via WebSocket")
                Connected_to_GR = True
                nb_erreur = 0
                while True:
                    raw = await websocket.recv()
                    spec = np.frombuffer(raw, dtype=np.float32)

                    # Convert to dB scale
                    spec_db = (10 * np.log10(spec + 1e-12)).astype(np.int8)

                    if len(spec_db) == 4096:
                        adr = packet_number * 4096
                        for i in range(4096):
                            # Mark sync at the START of the frame, not the center
                            if i in (0, 1):
                                byte_array[adr] = 255
                            else:
                                byte_array[adr] = spec_db[i]
                            adr += 1
                        packet_number = (packet_number + 1) % 16
                        nb_erreur = 0
                    else:
                        print("Unexpected packet size:", len(spec_db))
        except Exception as e:
            print("WebSocket error:", e)
            Connected_to_GR = False
            nb_erreur += 1
            await asyncio.sleep(0.1)

      

async def handle_Local_Server(reader, writer):   
   
    try :
       
        data = await reader.read(100)
        message_not_used = data.decode().strip()
        await send_Packet(writer)
    except:
        print("erreur connection vers web server")
        await asyncio.sleep(0.2)
    
      
async def send_Packet(writer): 
    global packet_number
    global byte_array
    pn_out=0
    adr0=0
    addr = writer.get_extra_info('peername')
    while True:
        while pn_out==packet_number :
            await asyncio.sleep(0.02)
        
        pn=packet_number
        adr1=pn*4096
        byte_array2 = bytearray()
        if adr1<adr0 :
            byte_array2[:]=byte_array[adr0:65536]
            byte_array2.extend(byte_array[0:adr1])
        else :
            byte_array2[:]=byte_array[adr0:adr1]
        
        writer.write(byte_array2)
        await writer.drain() 
        pn_out=pn
        adr0=adr1
        # writer.close() NEVER STOP
        await asyncio.sleep(0.02)    

async def main_Local_Server():
    
    server = await asyncio.start_server(handle_Local_Server, "127.0.0.1", port_spectre_web)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:        
        await server.serve_forever()		
		

loop = asyncio.get_event_loop()

loop.run_until_complete(asyncio.gather(main_Local_Server(),read_maia_Spectre()))
loop.run_forever()
loop.close()
