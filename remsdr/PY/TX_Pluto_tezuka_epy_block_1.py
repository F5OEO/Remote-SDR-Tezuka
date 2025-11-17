import subprocess
import numpy as np
from gnuradio import gr
import sys, threading, time
import adi

# Adjust your path as needed
sys.path.append("/home/analog/maia")
from maialib4 import MaiaPerParamClient, MaiaAPIError

class blk(gr.basic_block):
    """Maia Destination control block (no stream I/O)"""

    def __init__(self,
                 frequency=1000e6,
                 txgain=50,
                 txon=0,
                 rfbandwidth=200e3,
                 ):
        gr.basic_block.__init__(self,
            name='MaiaTx',
            in_sig=[],
            out_sig=[]
        )

        
        self.frequency = frequency

        self.client = None
        self._running = False
        self.txgain = txgain
        self.txon = txon
        self.rfbandwidth=rfbandwidth
        print("Init: Frequency setting", self.frequency, flush=True)
        self.sdr = None
        self.init()
        self.start()

    # --- Runtime setters (callbacks GRC will call) ---
    def set_frequency(self, frequency):
        self.frequency = frequency
        self.sdr.tx_lo = self.frequency 
        print("Frequency updated:", frequency, flush=True)

   
    def set_txgain(self, txgain):
           self.txgain = txgain
           hardwaregain=str(-float(89-self.txgain)) 
           tx_chan = self.phy.find_channel("voltage0", True) 
           tx_chan.attrs["hardwaregain"].value=hardwaregain
           print("TXGain updated:", hardwaregain, flush=True) 
    
    def set_txon(self, txon):
           self.txon = txon
           tx_chan = self.phy.find_channel("altvoltage1", True) 
           try:
               if txon is True:
                    tx_chan.attrs["powerdown"].value="0"
               else:
                    tx_chan.attrs["powerdown"].value="1"
           except Exception as e:
             print("Warning: TXON:", e, flush=True)
     
           print("Txon updated:", self.txon, flush=True) 

    def set_rfbandwidth(self, txon):
           
           self.sdr.tx_rf_bandwidth = self.rfbandwidth

    # --- Lifecycle hooks ---
    def init(self):
        
        print("Starting TX:") 
        try:
            self.sdr=adi.ad9361(uri="local:")
            self.ctx= self.sdr.ctx
            self.phy=self.ctx.find_device("ad9361-phy")
            tx_chan = self.phy.find_channel("altvoltage1", True) 
            
            # Force Interpolator x32
            subprocess.run(["busybox", "devmem", "0x790240BC", "32", "0x1"])
        except Exception as e:
            print("Warning: SDR init failed:", e, flush=True)
    
    def start(self):
        self._running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        return super().start()

    def run(self):
        while self._running:
            time.sleep(0.2)
            self.set_txon(self.txon)
            self.set_txgain(self.txgain)
            subprocess.run(["busybox", "devmem", "0x790240BC", "32", "0x1"])
            #interp=subprocess.run(["busybox", "devmem", "0x790240BC"])
            #print("Interp ",interp)        

    def stop(self):
        self._running = False
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join()
        return super().stop()

    
