import subprocess
import numpy as np
from gnuradio import gr
import sys, threading, time

# Adjust your path as needed
sys.path.append("/home/analog/maia")
from maialib4 import MaiaPerParamClient, MaiaAPIError

class blk(gr.basic_block):
    """Maia Source control block (no stream I/O)"""

    def __init__(self,
                 frequency=1000e6,
                 frequency_nco=0,
                 samplerate=1.2e6,
                 rxgain=50,                                  
                 url="http://127.0.0.1:8000"):
        gr.basic_block.__init__(self,
            name='Maia Source',
            in_sig=[],
            out_sig=[]
        )

        self.url = url
        self.frequency = frequency
        self.frequency_nco = frequency_nco
        self.samplerate = samplerate
        self.decim = int(samplerate/200e3)
        self.client = None
        self._running = False
        self.rxgain = rxgain

        print("Init: Frequency setting", self.frequency, flush=True)
        self.start()

    # --- Runtime setters (callbacks GRC will call) ---
    def set_frequency(self, frequency):
        self.frequency = frequency
        if self.client:
            try:
                self.client.set_rx_lo_frequency(frequency)
            except MaiaAPIError as e:
                print("Failed to set frequency:", e, flush=True)
        print("Frequency updated:", frequency, flush=True)

    def set_frequency_nco(self, frequency_nco):
        self.frequency_nco = frequency_nco
        if self.client:
            try:
                self.client.set_ddc_frequency(frequency_nco)
            except MaiaAPIError as e:
                print("Failed to set NCO:", e, flush=True)
        print("Frequency NCO updated:", frequency_nco, flush=True)

    def set_samplerate(self, samplerate):
        self.samplerate = samplerate
        client.set_sampling_frequency(self.samplerate)
        client.set_rx_rf_bandwidth(self.samplerate)
        print("Samplerate updated:", samplerate, flush=True)
    
    def set_rxgain(self, rxgain):
           self.rxgain = rxgain
           client.set_rx_gain_mode("Manual")
           client.set_rx_gain(self.rxgain)

    def set_decim(self, decim):
        self.decim = decim
        print("Decimation updated:", decim, flush=True)

    # --- Lifecycle hooks ---
    def start(self):
        print ("Starting", self.url)
        
        self.client = MaiaPerParamClient(self.url)
        try:
            self.client.set_rx_lo_frequency(self.frequency)
            self.client.put_ddc_design_params(
                self.frequency_nco,
                self.decim,
                0.05, 0.01, 50, True
            )
        except MaiaAPIError as e:
            print("Failed to configure Maia client:", e, flush=True)

        subprocess.run(["busybox", "devmem", "0x790200BC", "32", "0x1"])
        self._running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        return super().start()

    def run(self):
        while self._running:
            time.sleep(1)

    def stop(self):
        self._running = False
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join()
        return super().stop()

