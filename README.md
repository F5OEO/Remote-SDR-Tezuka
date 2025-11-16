## RemoteSDR for Tezuka

## Intro

This is a fork from F1ATB RemoteSDR. It has been optimized to run directly on the pluto plateform.

No need for extra Raspeberry pi or Orange pi. You just need a web browser (PC,Phone,Tablet...) and compatible sdr with sd card.

## HOWTO 

Download an available firmware at https://github.com/F5OEO/adi-kuiper-gen . This software is included and allows to use the custom fpga dsp.

## DISCLAIMER

Even some files remains about other SDRs (rtlsdr,hackrf..) ,this fork works ONLY on pluto embedded plateform.

## DOCUMENTATION

Most of the features are documented on original author : https://f1atb.fr/remote-sdr-v5-2/

Skip all the installation instructions as the software is already preinstalled.

## FUTURE

It was a good exercice to optimized Gnuradio flows, write embedded python code to use maia-sdr fpga faculities.

Python, NodeJS, Gnuradio, XML RPC and translating tcp to websocket could be done with more recent technics.

Using DSP on browser using jscript or wasm could offload the poor sdr embeded arm. 

Next generation could be started with nice projects like https://github.com/jtarrio/webrtlsdr






