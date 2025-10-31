import numpy as np
import asyncio
import threading
import websockets
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, ws_address="ws://127.0.0.1:8000/waterfall", fft_size=4096):
        gr.sync_block.__init__(
            self,
            name="WebSocket FFT Receiver",
            in_sig=None,
            out_sig=[(np.int16, fft_size // 2)]  # vector output of fft_size/2
        )
        self.ws_address = ws_address
        self.fft_size = fft_size
        self.buffer = None
        self.lock = threading.Lock()
        self.running = True

    def start(self):
        def runner():
            asyncio.run(self.spectrum_loop())
        self.thread = threading.Thread(target=runner, daemon=True)
        self.thread.start()
        return super().start()

    def stop(self):
        self.running = False
        return super().stop()

    async def spectrum_loop(self):
        async with websockets.connect(self.ws_address) as ws:
            while self.running:
                raw = await ws.recv()
                spec = np.frombuffer(raw, dtype=np.float32)

                # Convert to dB scale (power spectrum)
                spec_db = 10 * np.log10(spec + 1e-12)

                with self.lock:
                    self.buffer = spec_db

    def work(self, input_items, output_items):
        out = output_items[0]
        with self.lock:
            if self.buffer is not None:
                # Take every other bin (fft_size/2 bins)
                db_half = self.buffer[::2][:self.fft_size // 2]

                # Apply scale factor 100, clip to int16 range, cast
                scaled = db_half * 100.0
                clipped = np.clip(scaled, -32768, 32767)
                out[0][:] = clipped.astype(np.int16)
            else:
                out[0][:] = np.zeros(self.fft_size // 2, dtype=np.int16)
        return 1


