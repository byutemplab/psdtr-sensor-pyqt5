import struct
import pyvisa as visa


def DoStuff():
    # Set the waveform to be the one just sent
    vi.write("C1:BSWV WVTP,SINE,FRQ,10.4,AMP,3,OFST,-2.5,PHSE, 20")


rm = visa.ResourceManager()
li = rm.list_resources()
for device in li:
    vi = rm.open_resource(device)
    try:
        DoStuff()
        break
    except:
        print("couldn't open")
        continue
