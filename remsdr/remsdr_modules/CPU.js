var Temperature = 0;
var Fan_State = "Off";
var Model = "";
var CPUshort = "";
var GPIO_Fan = "73"; //Pin 7 on Orange Pi Zero 2(when CPU overheats) or Pin 12 Orange Pi One Plus
var GPIO_Oscil = "227"; // pin 26 in Orange PI One PLUS H6
const cp = require('child_process');
//const Gpio = require('onoff').Gpio; //to interact with the GPIO
const fs = require('fs');
var info_cpu = cp.execSync("lscpu").toString();
if (info_cpu.indexOf("armv7l") > 0) {
    Model = "Raspberry PI4";
    CPUshort = "RPI4";
    GPIO_Fan = "4"; // Pin 7 on Raspberry
    GPIO_Oscil = "7";
}
if (info_cpu.indexOf("aarch64") > 0) {
    Model = "Orange PI Zero One Plus";
    CPUshort = "opi1p";
    if (info_cpu.indexOf("1512.0") > 0) {
        Model = "Orange PI Zero 2";
        CPUshort = "opiz2";
        GPIO_Oscil = "74";
    }
}
// disable
// var Fan_Pin = new Gpio(GPIO_Fan, 'out');

function ReadTemperature() {
    var adr_Temp = '/sys/class/thermal/thermal_zone0/temp';
    fs.readFile(adr_Temp, 'utf8', function (err, data) { //Asynchrone read
        var T = Math.floor(parseInt(data) / 1000);
        Temperature = T + '°C';
        if (T >= 65) {
	    // disable
            //Fan_Pin.write(1);
            Fan_State = "On";
        } else {
	    // disable
            //Fan_Pin.write(0);
            Fan_State = "Off";
        }
    });
}
//
//Oscillator when TX
//*******************

//var Oscil_Pin = new Gpio(GPIO_Oscil, 'out');
var Oscil_state = 0;
//Oscil_Pin.write(Oscil_state);

function ToggleOscil() {
    Oscil_state = (Oscil_state + 1) % 2;
    //Oscil_Pin.write(Oscil_state);
}
var Oscil_interval;
function ToggleOscil_10s() {
    Oscil_interval = setInterval(ToggleOscil, 12);
    setTimeout(Oscil_Clear, 10000);
}
function Oscil_Clear() {
    clearInterval(Oscil_interval);
    //Oscil_Pin.write(0);
}
//
// GPIO setActive
// **************
function SetGPIOs(s) {
    

}

//
// SDR Management
//***************
var SDRrx = "";
var SDRtx = "";
var hackrf_info = "";
function Def_SDR() {
    
    var SDRs = [];
    try {
        SDRrx = fs.readFileSync('/remsdr/data/SDRrx.txt', 'utf8');
    } catch (e) {}
    try {
        SDRtx = fs.readFileSync('/remsdr/data/SDRtx.txt', 'utf8');
    } catch (e) {}
    
    SDRs.push("pluto|Adalm Pluto");
    if (SDRrx.length < 2)
       SDRrx = "pluto";
    if (SDRtx.length < 2)
        SDRtx = "pluto";
    
    SetSDR("RX", SDRrx);
    SetSDR("TX", SDRtx);
    return SDRs;
}
function SetSDR(Which, Type) {
    if (Which == "RX") {
        fs.writeFileSync('/remsdr/data/SDRrx.txt', Type);
    } else {
        fs.writeFileSync('/remsdr/data/SDRtx.txt', Type);
    }
}
function LastInfoCPU() {
    SDRs = Def_SDR();
    return {
        Temperature: Temperature,
        Fan_State: Fan_State,
        Model: Model,
        SDRs: SDRs,
        SDRrx: SDRrx,
        SDRtx: SDRtx,
        CPUshort: CPUshort
    }
}
module.exports = {
    LastInfoCPU,
    SetSDR,
    ToggleOscil,
    ToggleOscil_10s,
    SetGPIOs
};
Def_SDR();
ReadTemperature();
setInterval(ReadTemperature, 30000);
