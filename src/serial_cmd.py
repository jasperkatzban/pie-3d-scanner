import serial

BAUD_RATE = 115200

class Serial_cmd:

    Arduino_IDs = ((0x2341, 0x0043), (0x2341, 0x0001),
                   (0x2A03, 0x0043), (0x2341, 0x0243),
                   (0x0403, 0x6001), (0x1A86, 0x7523))

    def __init__(self, port = ''):  
        if port == '':
            self.dev = None
            self.connected = False
            devices = serial.tools.list_ports.comports()
            for device in devices:
                if (device.vid, device.pid) in Serial_cmd.Arduino_IDs:
                    try:
                        self.dev = serial.Serial(device.device, BAUD_RATE)
                        self.connected = True
                        print(f'Connected to {device.device}')
                    except:
                        print('Could not connect to device!')
                if self.connected:
                    break
        else:
            try:
                self.dev = serial.Serial(port, BAUD_RATE)
                self.connected = True
            except:
                self.dev = None
                self.connected = False

    def write(self, command):
        if self.connected:
            self.dev.write('{!s}\r'.format(command).encode())

    def read(self):
        if self.connected:
            return self.dev.readline().decode()