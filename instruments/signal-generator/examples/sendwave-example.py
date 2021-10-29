import struct
import pyvisa as visa

rm = visa.ResourceManager()
li = rm.list_resources()
for index in range(len(li)):
    print(str(index)+" - "+li[index])
choice = input("Which device?: ")
vi = rm.open_resource(li[int(choice)])

# vi.write_raw called from the vi.write needs the encoding changed
vi.encoding = 'latin-1'

print(vi.query("*idn?"))

wave = bytearray()

for i in range(16384):
    wave.append(i & 0xff)
    wave.append((i*7 & 0x3f00) >> 8)

# the next commands should not be terminated with newline char
vi.write_termination = ''

cmd = "C1:WVDT WVNM,santi,TYPE,5,LENGTH,32KB,FREQ,1000.0,AMPL,2,OFST,0,PHASE,0.000000,WAVEDATA," + \
    wave.decode('latin-1')
vi.write(cmd)
# the next commands should be terminated with newline char
vi.write_termination = '\n'
# vi.write("C1:ARWV INDEX, 101")  # Set the waveform to be the one just sent
vi.write("C1:MDWV AM, MDSP,SINE")


# the next commands should not be terminated with newline char
vi.write_termination = ''
# Note, the return value shows mXX+6, so m36 => M42
resp = vi.query("wvdt? USER,santi")

print("returned....")
print(len(resp))
# Print out the data
for i in range(96):
    print(":", i, resp[i], ord(resp[i]), sep="_", end='')
