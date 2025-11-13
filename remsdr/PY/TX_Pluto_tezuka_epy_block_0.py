import numpy as np
from gnuradio import gr

class phase_diff_approx(gr.sync_block):
    def __init__(self, harmonic=1.0):
        gr.sync_block.__init__(self,
            name="PhaseDiffApprox",
            in_sig=[np.complex64],    # complex32 input
            out_sig=[np.complex64])   # complex32 output

        self.prev = None
        self.harmonic = harmonic     # coefficient multiplier

    def set_harmonic(self, harmonic):
        """Runtime setter so GRC can update the parameter"""
        self.harmonic = harmonic
        print("Harmonic coefficient updated:", harmonic, flush=True)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        for i, x in enumerate(in0):
            if self.prev is None:
                out[i] = x
            else:
                # Conjugate product
                prod = x * np.conj(self.prev)

                # Approximate phase difference (no atan2)
                denom = np.abs(x) * np.abs(self.prev)
                if denom == 0:
                    delta_phi = 0.0
                else:
                    delta_phi = np.imag(prod) / denom

                # Preserve amplitude and apply harmonic multiplier
                amp = np.abs(x)
                out[i] = amp * np.exp(1j * self.harmonic * delta_phi)

            self.prev = x

        return len(out)

