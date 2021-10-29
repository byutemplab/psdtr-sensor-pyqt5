# This example uses the Python package PyVisa and depends on a version of VISA driver be installed
# B+K Recommends users to use the VISA drivers from National Instruments aka. NI-VISA
import time
import pyvisa as visa
rm = visa.ResourceManager()
li = rm.list_resources()
for index in range(len(li)):
    print(str(index)+" - "+li[index])
choice = input("Which device?: ")
vi = rm.open_resource(li[int(choice)])

print(vi.query("*idn?"))

print("Configuring C1")
vi.write("c1:bswv frq,1000")  # set the frequency of channel 1
vi.write("c1:bswv wvtp,SINE")  # set the type of waveform
vi.write("c1:bswv duty,75")  # duty cycle

# enable the waveform output, wait and disable the output
vi.write("c1:output on")
print("Output on")
time.sleep(5)
vi.write("c1:output off")
print("Output off")
time.sleep(1)
