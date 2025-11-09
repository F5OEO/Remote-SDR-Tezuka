#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SSB NBFM Transmitter
# Author: F5OEO
# Copyright: GNU General Public Licence v3.0
# Description: TX SSB NBFM tezuka
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
from gnuradio import network
from xmlrpc.server import SimpleXMLRPCServer
import threading
import TX_Pluto_tezuka_epy_block_1 as epy_block_1  # embedded python block




class TX_Pluto_tezuka(gr.top_block):

    def __init__(self, SampRate=1600000, baseband=10000, device=''):
        gr.top_block.__init__(self, "SSB NBFM Transmitter", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.SampRate = SampRate
        self.baseband = baseband
        self.device = device

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = SampRate
        self.maia_url = maia_url = "http://127.0.0.1:8000"
        self.LNUC = LNUC = 0
        self.G2 = G2 = 0
        self.G1 = G1 = 70
        self.Fsdr = Fsdr = 432100000

        ##################################################
        # Blocks
        ##################################################
        self.xmlrpc_server_0 = SimpleXMLRPCServer(('localhost', 19004), allow_none=True)
        self.xmlrpc_server_0.register_instance(self)
        self.xmlrpc_server_0_thread = threading.Thread(target=self.xmlrpc_server_0.serve_forever)
        self.xmlrpc_server_0_thread.daemon = True
        self.xmlrpc_server_0_thread.start()
        self.rational_resampler_xxx_1_1 = filter.rational_resampler_ccc(
                interpolation=int(samp_rate/(baseband*8)),
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_1_0 = filter.rational_resampler_ccc(
                interpolation=int(samp_rate/(baseband*5*8)),
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_1 = filter.rational_resampler_ccc(
                interpolation=int(samp_rate/(baseband*8)),
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.network_udp_source_0 = network.udp_source(gr.sizeof_short, 1, 19005, 0, 128, False, False, False)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('local:' if 'local:' else iio.get_pluto_uri(), [True, True], 32000, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(int(samp_rate))
        self.iio_pluto_sink_0.set_frequency(Fsdr)
        self.iio_pluto_sink_0.set_samplerate(int(samp_rate))
        self.iio_pluto_sink_0.set_attenuation(0, 0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.iio_attr_sink_0 = iio.attr_sink('local:', 'ad9361-phy', 'voltage0', 0, True)
        self.hilbert_fc_0 = filter.hilbert_fc(64, window.WIN_HAMMING, 6.76)
        self.hilbert_fc_0.set_min_output_buffer(10)
        self.hilbert_fc_0.set_max_output_buffer(10)
        self.epy_block_1 = epy_block_1.blk(frequency=Fsdr, samplerate=samp_rate, txgain=G1, baseband=baseband, url=maia_url)
        self.epy_block_1.set_block_alias("MaiaTX")
        self.blocks_var_to_msg_0 = blocks.var_to_msg_pair('hardwaregain')
        self.blocks_short_to_float_0 = blocks.short_to_float(1, 32767)
        self.blocks_selector_1 = blocks.selector(gr.sizeof_gr_complex*1,abs(LNUC),0)
        self.blocks_selector_1.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_float*1,0,abs(LNUC))
        self.blocks_selector_0.set_enabled(True)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(LNUC)
        self.blocks_message_debug_0 = blocks.message_debug(True)
        self.blocks_float_to_complex_0_0 = blocks.float_to_complex(1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.band_pass_filter_0_0 = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1,
                baseband,
                300,
                3500,
                1200,
                window.WIN_HAMMING,
                6.76))
        self.band_pass_filter_0 = filter.fir_filter_ccc(
            1,
            firdes.complex_band_pass(
                1,
                baseband,
                -1300+LNUC*1500,
                1300+LNUC*1500,
                200,
                window.WIN_HAMMING,
                6.76))
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=baseband,
        	quad_rate=int(baseband*5),
        	tau=75e-6,
        	max_dev=5e3,
        	fh=-1.0,
                )
        self.analog_const_source_x_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_var_to_msg_0, 'msgout'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.blocks_var_to_msg_0, 'msgout'), (self.iio_attr_sink_0, 'attr'))
        self.connect((self.analog_const_source_x_1, 0), (self.blocks_float_to_complex_0_0, 1))
        self.connect((self.analog_nbfm_tx_0, 0), (self.rational_resampler_xxx_1_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.analog_nbfm_tx_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_float_to_complex_0_0, 0), (self.rational_resampler_xxx_1_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_selector_0, 0), (self.band_pass_filter_0_0, 0))
        self.connect((self.blocks_selector_0, 2), (self.blocks_float_to_complex_0_0, 0))
        self.connect((self.blocks_selector_0, 1), (self.hilbert_fc_0, 0))
        self.connect((self.blocks_selector_1, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.blocks_short_to_float_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.hilbert_fc_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.network_udp_source_0, 0), (self.blocks_short_to_float_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.blocks_selector_1, 1))
        self.connect((self.rational_resampler_xxx_1_0, 0), (self.blocks_selector_1, 0))
        self.connect((self.rational_resampler_xxx_1_1, 0), (self.blocks_selector_1, 2))


    def get_SampRate(self):
        return self.SampRate

    def set_SampRate(self, SampRate):
        self.SampRate = SampRate
        self.set_samp_rate(self.SampRate)

    def get_baseband(self):
        return self.baseband

    def set_baseband(self, baseband):
        self.baseband = baseband
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.baseband, -1300+self.LNUC*1500, 1300+self.LNUC*1500, 200, window.WIN_HAMMING, 6.76))
        self.band_pass_filter_0_0.set_taps(firdes.band_pass(1, self.baseband, 300, 3500, 1200, window.WIN_HAMMING, 6.76))
        self.epy_block_1.baseband = self.baseband

    def get_device(self):
        return self.device

    def set_device(self, device):
        self.device = device

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.epy_block_1.samplerate = self.samp_rate
        self.iio_pluto_sink_0.set_bandwidth(int(self.samp_rate))
        self.iio_pluto_sink_0.set_samplerate(int(self.samp_rate))

    def get_maia_url(self):
        return self.maia_url

    def set_maia_url(self, maia_url):
        self.maia_url = maia_url
        self.epy_block_1.url = self.maia_url

    def get_LNUC(self):
        return self.LNUC

    def set_LNUC(self, LNUC):
        self.LNUC = LNUC
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.baseband, -1300+self.LNUC*1500, 1300+self.LNUC*1500, 200, window.WIN_HAMMING, 6.76))
        self.blocks_multiply_const_vxx_0.set_k(self.LNUC)
        self.blocks_selector_0.set_output_index(abs(self.LNUC))
        self.blocks_selector_1.set_input_index(abs(self.LNUC))

    def get_G2(self):
        return self.G2

    def set_G2(self, G2):
        self.G2 = G2

    def get_G1(self):
        return self.G1

    def set_G1(self, G1):
        self.G1 = G1
        self.blocks_var_to_msg_0.variable_changed(str(-float(89-self.G1)))
        self.epy_block_1.txgain = self.G1

    def get_Fsdr(self):
        return self.Fsdr

    def set_Fsdr(self, Fsdr):
        self.Fsdr = Fsdr
        self.epy_block_1.frequency = self.Fsdr
        self.iio_pluto_sink_0.set_frequency(self.Fsdr)



def argument_parser():
    description = 'TX SSB NBFM tezuka'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--SampRate", dest="SampRate", type=eng_float, default=eng_notation.num_to_str(float(1600000)),
        help="Set SampRate [default=%(default)r]")
    parser.add_argument(
        "--baseband", dest="baseband", type=eng_float, default=eng_notation.num_to_str(float(10000)),
        help="Set baseband [default=%(default)r]")
    parser.add_argument(
        "--device", dest="device", type=str, default='',
        help="Set device [default=%(default)r]")
    return parser


def main(top_block_cls=TX_Pluto_tezuka, options=None):
    if options is None:
        options = argument_parser().parse_args()
    tb = top_block_cls(SampRate=options.SampRate, baseband=options.baseband, device=options.device)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    tb.wait()


if __name__ == '__main__':
    main()
