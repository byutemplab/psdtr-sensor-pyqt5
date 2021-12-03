import pyvisa as visa


class WaveformGenerator():
    def __init__(self):
        self.connected = False
        self.to_cmd = {
            'Sine':     'SINE',
            'Square':   'SQUARE',
            'Triangle': 'RAMP',
        }

    def Send(self, waveform, frequency, amplitude, offset, phase):
        # If not connected, try to connect
        if not self.connected:
            self.connected = self.Connect()

        # If connected, try to send
        if self.connected:
            try:
                cmd = ("C1:BSWV WVTP," + self.to_cmd[waveform] +
                       ",FRQ," + str(frequency) +
                       ",AMP," + str(amplitude) +
                       ",OFST," + str(offset) +
                       ",PHSE," + str(phase))
                self.device.write(cmd)
            except:
                print("Couldn't find waveform generator")
                self.connected = False

    def Connect(self):
        rm = visa.ResourceManager()
        li = rm.list_resources()
        for resource in li:
            device = rm.open_resource(resource)
            try:
                device.query("*idn?")
                self.device = device
                return True
            except:
                print("Couldn't find waveform generator")
                continue

        return False
