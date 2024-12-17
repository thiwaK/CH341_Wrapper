import ctypes
from ctypes import c_ulong, cast, byref, Structure#,create_string_buffer
from ctypes import POINTER, c_uint, c_bool, c_void_p, c_byte, c_char, c_char_p
import struct
from io import BytesIO, BufferedReader, SEEK_END, SEEK_SET
import time
import zlib



CH341DLL = ctypes.WinDLL("CH341")



WRITE_ENABLE = 0X06
WRITE_DISABLE = 0X04
READ_STATUS_REG1 = 0X05
READ_STATUS_REG2 = 0X35
EWSR = 0X50
PAGE_PROGRAM = 0X02

SECTOR_ERASE_4K = 0X20
BLOCK_ERASE_32K = 0X52
BLOCK_ERASE_64K = 0XD8
CHIP_ERASE = 0XC7

READ_FROM_CACHE_X4 = 0x6B
READ_FROM_CACHE_X2 = 0x3B
READ_FROM_CACHE = 0x0B
READ_DATA = 3

ENABLE_4BIT_MODE = 183
DISABLE_4BIT_MODE = 233
VENDOR_READ = 0xC0

SPEED_LOW = 0b00000000 #  20KHz
SPEED_STANDARD = 0b01000000 # 100KHz
SPEED_FAST = 0b10000000 # 400KHz
SPEED_HIGH = 0b11000000 # 750KHz
SPI_IO_SINGLE = 0b00000000 # single input and single output
SPI_IO_DOUBLE = 0b00100000 # double input and double output
SPI_BIT_ORDER_LITTLE = 0b00000000 # little-endian (Low end first)
SPI_BIT_ORDER_BIG = 0b00000001 # big-endian (High end first)

"""
0x29, 1 - 00101001
0x29, 0 - 00101001
0x00, 0 - 
0x3F, 0 - 00111111

"""


class CH341:

    CH341DLL.CH341OpenDevice.argtypes = [c_uint]
    CH341DLL.CH341OpenDevice.restype = c_void_p

    CH341DLL.CH341CloseDevice.argtypes = [c_uint]
    CH341DLL.CH341CloseDevice.restype = None

    CH341DLL.CH341GetVersion.argtypes = []
    CH341DLL.CH341GetVersion.restype = None

    CH341DLL.CH341GetDeviceName.argtypes = [c_ulong]
    CH341DLL.CH341GetDeviceName.restype = c_void_p 

    CH341DLL.CH341DriverCommand.argtypes = [c_uint, c_void_p]
    CH341DLL.CH341DriverCommand.restype = None

    CH341DLL.CH341SetDeviceNotify.argtypes = [c_uint, c_void_p, c_void_p]
    CH341DLL.CH341SetDeviceNotify.restype = c_uint

    CH341DLL.CH341WriteData.argtypes = [c_uint, c_void_p, c_void_p]
    CH341DLL.CH341WriteData.restype = c_bool

    CH341DLL.CH341GetVerIC.argtypes = [c_uint]
    CH341DLL.CH341GetVerIC.restype = c_uint

    CH341DLL.CH341SetStream.argtypes = [c_ulong, c_ulong]
    CH341DLL.CH341SetStream.restype = c_bool

    CH341DLL.CH341Set_D5_D0.argtypes = [c_ulong, c_ulong, c_ulong]
    CH341DLL.CH341Set_D5_D0.restype = c_bool

    CH341DLL.CH341SetDelaymS.argtypes = [c_uint, c_uint]
    CH341DLL.CH341SetDelaymS.restype = c_bool

    CH341DLL.CH341SetExclusive.argtypes = [c_uint, c_uint]
    CH341DLL.CH341SetExclusive.restype = c_bool

    CH341DLL.CH341StreamSPI5.argtypes = [c_uint, c_uint, c_uint, c_void_p, c_void_p]
    CH341DLL.CH341StreamSPI5.restype = c_bool

    CH341DLL.CH341StreamSPI4.argtypes = [c_uint, c_uint, c_uint, c_void_p]
    CH341DLL.CH341StreamSPI4.restype = c_bool

    CH341DLL.CH341BitStreamSPI.argtypes = [c_uint, c_uint, c_void_p]
    CH341DLL.CH341BitStreamSPI.restype = c_bool

    CH341DLL.CH341StreamSPI3.argtypes = [c_uint, c_uint, c_uint, c_void_p]
    CH341DLL.CH341StreamSPI3.restype = c_bool

    CH341DLL.CH341WriteRead.argtypes = [
        c_ulong,                
        c_ulong,                
        c_void_p,               
        c_ulong,                
        c_ulong,                
        c_ulong,       
        c_void_p                
    ]
    CH341DLL.CH341WriteRead.restype = c_bool

    @staticmethod
    def setStream(iIndex, iMode):
        """
        BOOL WINAPI CH341SetStream( // Set the serial port stream mode
        ULONG iIndex,           // Specify CH341 device serial number
        ULONG iMode );          // Specify mode

        Mode:
         Bit 1-Bit 0: I2C interface speed/SCL frequency
            00=low speed/20KHz
            01=standard/100KHz (default value)
            10=fast/400KHz
            11=high speed/750KHz
         Bit 2: SPI I/O number/IO pin
            0=single input and single output (D3 clock/D5 output/D7 input) (default value)
            1=double input and double output (D3 clock/D5 output D4 Out/D7 in D6 in)
         Bit 7: Bit order in SPI byte
            0=low end first
            1=high end first
         
         Other bits reserved, must be 0
        """
        if not CH341DLL.CH341SetStream(c_ulong(iIndex), c_ulong(iMode)):
            raise RuntimeError("CH341SetStream")

    @staticmethod
    def setD5D0(iIndex, iSetDirOut, iSetDataOut):
        """
        BOOL    WINAPI  CH341Set_D5_D0(  // Set the I/O direction of the D5-D0 pin of CH341, and directly output data through the D5-D0 pin of CH341, which is more efficient than CH341SetOutput
        /* ***** Use this API with caution to prevent changing the I/O direction to change the input pin into an output pin, resulting in a short circuit with other output pins and damaging the chip ***** */
            ULONG           iIndex,  // Specify CH341 device serial number
            ULONG           iSetDirOut,  // Set the I/O direction of each pin of D5-D0. If a certain bit is cleared to 0, the corresponding pin is input, and if a certain bit is set to 1, the corresponding pin is output. The default value in parallel port mode is 0x00, all input
            ULONG           iSetDataOut );  // Set the output data of each pin of D5-D0. If the I/O direction is output, then when a certain bit is cleared to 0, the corresponding pin outputs a low level, and when a certain bit is set to 1, the corresponding pin outputs a high level.
        // Bit 5-bit 0 of the above data correspond to the D5-D0 pins of CH341 respectively.
        """ 
        if not CH341DLL.CH341Set_D5_D0(c_ulong(iIndex), c_ulong(iSetDirOut), c_ulong(iSetDataOut)):
            raise RuntimeError("CH341Set_D5_D0")

    @staticmethod
    def streamSPI4(iIndex, iChipSelect, iLength, ioBuffer):
        """
        BOOL    WINAPI  CH341StreamSPI4(  // Process SPI data stream, 4-wire interface, the clock line is DCK/D3 pin, the output data line is DOUT/D5 pin, the input data line is DIN/D7 pin, and the chip select line is D0/ D1/D2, speed is about 68K bytes
        /* SPI timing: The DCK/D3 pin is the clock output, which defaults to low level. The DOUT/D5 pin outputs during the low level before the rising edge of the clock. The DIN/D7 pin outputs the high level before the falling edge of the clock. Enter during normal times */
        ULONG           iIndex,  // Specify CH341 device serial number
        ULONG           iChipSelect,  // Chip select control, if bit 7 is 0, the chip select control is ignored, if bit 7 is 1, the parameters are valid: Bit 1 and bit 0 are 00/01/10, respectively, select the D0/D1/D2 pin as low level. valid chip select
        ULONG           iLength,  // Number of data bytes to be transmitted
        PVOID           ioBuffer );  // Point to a buffer, place the data to be written from DOUT, and return the data read from DIN
        """
        if not CH341DLL.CH341StreamSPI4(c_ulong(iIndex), c_ulong(iChipSelect), c_ulong(iLength), ioBuffer):
            raise RuntimeError("CH341StreamSPI4")

    @staticmethod
    def setDelaymS(iIndex, iDelay):
        """
        BOOL WINAPI CH341SetDelaymS(    // Set the hardware asynchronous delay, return soon after the call, and delay the specified number of milliseconds before the next stream operation
        ULONG iIndex,               //Specify CH341 device serial number
        ULONG iDelay );             //Specify the number of milliseconds of delay   
        """
        if not CH341DLL.CH341SetDelaymS(c_uint(iIndex), c_uint(iDelay)):
            raise RuntimeError("CH341SetDelaymS")

class Util:

    def write_to(self, file_name='out.bin', data=None):
        with open(file_name, 'wb') as f:
            f.write(data)

    def read_from(self, file_name='out.bin'):
        with open(file_name, 'rb') as f:
            return f.read()

    def convert_size(self, byte_size):
        if byte_size < 1024:
            return f"{byte_size} Bytes"
        elif byte_size < 1024**2:
            kb_size = byte_size / 1024
            return f"{kb_size:.2f} KB"
        elif byte_size < 1024**3:
            mb_size = byte_size / 1024**2
            return f"{mb_size:.2f} MB"
        else:
            gb_size = byte_size / 1024**3
            return f"{gb_size:.2f} GB"

    def format_time(self, milliseconds):
        minutes = milliseconds // 60000  # 1 minute = 60,000 milliseconds
        seconds = (milliseconds % 60000) // 1000  # Remaining seconds
        millis = milliseconds % 1000  # Remaining milliseconds

        if minutes > 0:
            return f"{minutes:.0f}m:{seconds:.0f}s:{millis:.0f}mi"
        elif seconds > 0:
            return f"{seconds:.0f}s:{millis:.0f}mi"
        else:
            return f"{millis:.1f}mi"



class Device:
    
    def __init__(self, OOB_SIZE=64, PAGE_SIZE=2048+64, BLOCK_SIZE=135168, BLOCKS_COUNT=1024):

        self.PAGE_SIZE = PAGE_SIZE
        self.BLOCK_SIZE = BLOCK_SIZE
        self.PAGE_OOB_SIZE = OOB_SIZE

        self.PAGE_DATA_SIZE = PAGE_SIZE - OOB_SIZE
        self.PAGES_PER_BLOCK = int(BLOCK_SIZE/PAGE_SIZE)
        self.CHIP_SIZE = BLOCK_SIZE * BLOCKS_COUNT

        self.util = Util()

    def byte_to_hex_string(self, values):
        
        hex_str = "".join([hex(x)[2:].upper() for x in values])
        if len(hex_str) % 2 > 0:
            hex_str = '0' + hex_str  # Add leading zero if the length is odd
        return hex_str
    
    def read_register_spi_25(self, register, operationCode=5):
        self.write_spi_341(0, 0, 1, bytes([operationCode]))
        return self.read_spi_341(1, 0, 1, register)

    def is_spi_25_busy(self):

        buffer = bytes([255])
        self.read_register_spi_25(buffer, READ_STATUS_REG1);

        return buffer[0] != 255
        
    def unlock_spi_chip_25(self):
        
        self.start_spi_mode_25();

        self.IsRunning = True 
        self.enable_write();
        
        self.write_spi_341(1, 0, 1, bytes([152]))

        print("Unlocking...")
        self.is_spi_25_busy()
        
        self.disable_write()
        self.stop_spi_mode_25()
            
        self.IsRunning = False
        print("Chip is unlocked.")
        

    def enable_write(self):
        self.write_spi_341(1, 0, 1, bytes([WRITE_ENABLE]))

    def disable_write(self):
        self.write_spi_341(1, 0, 1, bytes([WRITE_DISABLE]))
        

    def enable_4bit_mode(self):
        self.write_spi_341(1, 0, 1, bytes([ENABLE_4BIT_MODE]))

    def disable_4bit_mode(self):
        self.write_spi_341(1, 0, 1, bytes([DISABLE_4BIT_MODE]))


    def read_spi_chip_id_341(self):

        memory_types = {
            0x01: "DRAM",
            0x02: "EEPROM",
            0x03: "Flash (NAND)",
            0x04: "SRAM",
            0x05: "ROM",
            0x20: "Flash (NOR)",
            0x30: "PCM (Phase-Change Memory)",
            0x40: "FRAM",
            0x50: "MRAM",
            0x60: "ReRAM"
        }


        self.IsRunning = True  # Set running flag

        self.start_spi_mode_25()
        str_id = self.read_id_spi_mode_25()
        self.stop_spi_mode_25()

        self.IsRunning = False




        result = self.byte_to_hex_string(str_id[0])
        maf_id, dev_type, dev_cap = result[1], result[2], result[3]

        buffer = bytes([0x9F, 0])
        self.write_spi_341(0, 0, 2, buffer)

        buffer = bytes([0]*3)
        self.read_spi_341(1, 0, 3, buffer)
        result = struct.unpack("3B", buffer)

        manufacturer_id = self.byte_to_hex_string([result[0]])
        devic_id = self.byte_to_hex_string([result[1], result[2]])

        # result = ''
        # dev_cap = str_id[2]
        # for x in dev_cap:
        #     result += self.byte_to_hex_string([x])
        # dev_cap = result

        # result = ''
        # dev_type = str_id[3]
        # for x in dev_type:
        #     result += self.byte_to_hex_string([x])
        # dev_type = result

        print(f"Manufacturer ID: {manufacturer_id}")
        print(f"Device ID: {devic_id}")
        # print(f"Memory Type: {dev_type}")
        # print(f"Memory Capacity: {dev_cap}")
        # print(f"Device UID: {dev_uid}")

        return

    def read_id_spi_mode_25(self):
        
        str_id = [None] * 4

        # Read Manufacturer and Device ID (JEDEC ID)
        '''
        https://www.jedec.org/document_search?search_api_views_fulltext=JEP106

        Manufacturer ID (1 byte)
        Memory Type (1 byte)
        Memory Density/Capacity (1 byte)
        '''
        buffer = bytes([0x9F])
        self.write_spi_341(0, 0, 1, buffer);
        buffer = bytes([0]*3)
        self.read_spi_341(1, 0, 3, buffer);
        str_id[0] = struct.unpack("3B", buffer)
        
        #  Read Manufacturer ID and Device ID (Legacy)
        buffer = bytes([0x90, 0, 0, 0])
        self.write_spi_341(0, 0, 4, buffer);
        buffer = bytes([0, 0])
        self.read_spi_341(1, 0, 2, buffer);
        str_id[1] = struct.unpack("BB", buffer)
        # print(buffer)

        # Read Manufacturer and Device ID (Alternate)
        buffer = bytes([0xAB, 0, 0, 0])
        self.write_spi_341(0, 0, 4, buffer);
        buffer = bytes([0])
        self.read_spi_341(1, 0, 2, buffer);
        str_id[2] = struct.unpack("B", buffer)
        # print(buffer)

        buffer = bytes([0x15])
        self.write_spi_341(0, 0, 1, buffer);
        buffer = bytes([0, 0])
        self.read_spi_341(1, 0, 2, buffer);
        str_id[3] = struct.unpack("BB", buffer)
        # print(buffer)

        
        return str_id


    def read_spi_341(self, value, index, buffer_len, buffer):

        # buffer_pointer = ctypes.cast(buffer, c_void_p)
        
        CH341.setD5D0(index, 63, 0)
        CH341.streamSPI4(index, 0, buffer_len, buffer)
        print(self.byte_to_hex_string(buffer[0:10]), self.byte_to_hex_string(buffer[-10:]), zlib.crc32(buffer))


        if value == 1:
            CH341.setD5D0(index, 63, 1)

        return buffer_len

    def write_spi_341(self, value, index, buffer_len, buffer):

        CH341.setD5D0(index, 41, 0)
        CH341.streamSPI4(index, 0, buffer_len, buffer)
        
        if value == 1:
            CH341.setD5D0(index, 41, 1)
        
        return buffer_len

    def erase_spi_chip_25(self):
        self.start_spi_mode_25()
        self.enable_write()

        self.write_spi_341(1, 0, 1, bytes([0x62])) # ATMEL
        self.write_spi_341(1, 0, 1, bytes([0x60])) # SST
        self.write_spi_341(1, 0, 1, bytes([0xC7])) # STANDARD

        while (self.is_spi_25_busy()):
            pass

        self.disable_write()
        self.stop_spi_mode_25()


    def read_32bit_address_spi25_341(self, address, page_size, buffer):

        """
        addr      com
        00000000  03000000
        00000840  03000840
        00001080  03001080
        000018C0  030018C0
        ...
        0000B580  0300B580
        """
        
        
        # Ensure the address is in the correct byte order (Big Endian format)
        byte_1 = (address >> 24) & 0xFF  # Most significant byte
        byte_2 = (address >> 16) & 0xFF  # Second byte
        byte_3 = (address >> 8) & 0xFF   # Third byte
        byte_4 = address & 0xFF          # Least significant byte
        
        print(f"Extracted bytes: {byte_1:02X} {byte_2:02X} {byte_3:02X} {byte_4:02X}")
        spi_write_buffer = bytes([READ_DATA, byte_1, byte_2, byte_3, byte_4])

        self.write_spi_341(0, 0, 5, spi_write_buffer)

        res = self.read_spi_341(1, 0, page_size, buffer)
        return res

    def read_16bit_address_spi25_341(self, address, page_size, buffer):

        spi_write_buffer = bytes([
            READ_DATA,
            (address & 0x00FF0000) >> 16,                 # Extract and shift the second byte
            (address & 0x0000FF00) >> 8,                  # Extract and shift the third byte
            address & 0x000000FF                          # Extract the least significant byte
        ])
    
        self.write_spi_341(0, 0, len(spi_write_buffer), spi_write_buffer)

        res = self.read_spi_341(1, 0, page_size, buffer)

        return res

    def write_32bit_address_spi25_341(self, address, page_size, buffer):
        # print(f"Writing {hex(address)} to {hex(address + page_size)}")
        spi_write_buffer = bytes([
            PAGE_PROGRAM,
            (address & 0xFF000000) >> 24,                 # Extract and shift the most significant byte
            (address & 0x00FF0000) >> 16,                 # Extract and shift the second byte
            (address & 0x0000FF00) >> 8,                  # Extract and shift the third byte
            address & 0x000000FF                          # Extract the least significant byte
        ])

        self.write_spi_341(0, 0, 5, spi_write_buffer)

        res = self.read_spi_341(1, 0, page_size, buffer)

        CH341.setDelaymS(0, 2)
        return res


    def stop_spi_mode_25(self):
        
        CH341.setD5D0(0, 0, 0)

    def start_spi_mode_25(self):
        
        CH341.setStream(0, 0x80)
        CH341.setDelaymS(0, 0x32)

        buffer = bytes([0xAB])
        self.write_spi_341(1, 0, 1, buffer)

        CH341.setDelaymS(0, 2)


    def read_page(self, start_page=0, end_page=1, file='out.bin', verbouse=True):
        
        FLASH_SIZE_128BIT = 16777216;
        bytesRead = 0

        address = 0
        iPageSize = self.PAGE_SIZE
        iChipSize = self.CHIP_SIZE

        if start_page != None and end_page != None and end_page > 0:
            address = start_page * self.PAGE_SIZE
            iPageSize = self.PAGE_SIZE
            iChipSize = end_page * self.PAGE_SIZE

        
        ms = BytesIO()


        if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
            self.enable_4bit_mode()

        if verbouse:
            print(f"Reading from page {start_page} to {end_page}")
            print(f"Reading time: {self.util.format_time(self.page_time_ms*(end_page - start_page))}")

        while (address < iChipSize):

            buffer = bytes([0 for x in range(self.PAGE_SIZE)])
            
            if (iPageSize > iChipSize - address):
                iPageSize = iChipSize - address

            if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
                bytesRead += self.read_32bit_address_spi25_341(address, iPageSize, buffer)
            else:
                bytesRead += self.read_16bit_address_spi25_341(address, iPageSize, buffer);
            
            ms.write(buffer)
            address += iPageSize

            del buffer

            

        if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
            self.disable_4bit_mode()

        result = ms.getvalue()
        ms.close()

        if file != None:
            self.util.write_to(file, data=result)
        if verbouse: 
            print(f"Total bytes read:", bytesRead, self.util.convert_size(bytesRead))
            print(f"Total data bytes:", bytesRead - ((bytesRead//self.PAGE_SIZE)*self.PAGE_OOB_SIZE), self.util.convert_size(bytesRead - ((bytesRead//self.PAGE_SIZE)*self.PAGE_OOB_SIZE)))
        return result

    def write_page(self, start_page=None, file=None, verify_write=True):
        
        FLASH_SIZE_128BIT = 16777216;
        bytesWrite = 0

        if start_page == None or file == None:
            raise ValueError("Did you forgot something?")

        data_stream = BytesIO(self.util.read_from(file))

        data_stream.seek(0, SEEK_END)
        iDataSize = data_stream.tell()
        data_stream.seek(0, SEEK_SET)
            
        address = start_page * self.PAGE_SIZE
        iPageSize = self.PAGE_SIZE
        iDataSize = address + iDataSize

        if verify_write:
            # print(f"reading from page {start_page} to {int(iDataSize/self.PAGE_SIZE)}")
            before_write = self.read_page(start_page, int(iDataSize/self.PAGE_SIZE), None, False)

        self.enable_write()

        if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
            self.enable_4bit_mode()

        print(f"Start writing {iDataSize-address} bytes from address {address}")

        while (address < iDataSize):
            
            if (iPageSize > iDataSize - address):
                iPageSize = iDataSize - address

            buffer = data_stream.read(iPageSize)

            if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
                bytesWrite += self.write_32bit_address_spi25_341(address, iPageSize, buffer)
            
            while (self.is_spi_25_busy()):
                print(self.is_spi_25_busy())
                time.sleep(0.5)
            

            address += iPageSize
            # print(f"Wrote {bytesWrite} bytes. Current address {address}")

        if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
            self.disable_4bit_mode()


        print(f"Total bytes write:", bytesWrite)
        self.disable_write()

        if verify_write:
            # print(f"reading from page {start_page} to {int(iDataSize/self.PAGE_SIZE)}")
            after_write = self.read_page(start_page, int(iDataSize/self.PAGE_SIZE), None, False)

            if before_write != after_write:
                print("Something changed")
            else:
                print("Nothing changed")

        return


    def read_bytes(self, from_offset, to_offset, exclude_oob=True, out=None):

        start_page, end_page = None, None
        if exclude_oob:
            start_page = from_offset // self.PAGE_DATA_SIZE
            end_page = (from_offset + to_offset) // self.PAGE_DATA_SIZE
        else:
            start_page = from_offset // self.PAGE_SIZE
            end_page = (from_offset + to_offset) // self.PAGE_SIZE

        return self.read_page(start_page, end_page, out)

    def write_bytes(self, from_offset, file=None, exclude_oob=True):

        start_page, end_page = None, None
        if exclude_oob:
            start_page = from_offset // self.PAGE_DATA_SIZE
        else:
            start_page = from_offset // self.PAGE_SIZE

        return self.write_page(start_page, file)


    def read_flash_bytes(self):

        buffer = bytes([32, 00, 00, 00, 00])
        self.write_spi_341(0, 0, 5, buffer);

        buffer = bytes([0]*2112)
        self.read_spi_341(1, 0, 2112, buffer);

        print(self.byte_to_hex_string(buffer[0:10]), self.byte_to_hex_string(buffer[-10:]), zlib.crc32(buffer))

        buffer = bytes([32, 00, 00, 0x08, 0x40])
        self.write_spi_341(0, 0, 5, buffer);

        buffer = bytes([0]*2112)
        self.read_spi_341(1, 0, 2112, buffer);

        print(self.byte_to_hex_string(buffer[0:10]), self.byte_to_hex_string(buffer[-10:]), zlib.crc32(buffer))



    def open(self, i_index, speed=SPEED_HIGH, spi_io=SPI_IO_SINGLE, spi_bit_order=SPI_BIT_ORDER_BIG):

        print("="*35)
        print(f"Chip size :", self.CHIP_SIZE, f"{int(self.CHIP_SIZE/1024/1024)}MBit")
        print(f"Block size:", self.BLOCK_SIZE, f"({self.PAGES_PER_BLOCK} pages)")
        print(f"Page size :", self.PAGE_SIZE, f"({self.PAGE_DATA_SIZE} + {self.PAGE_OOB_SIZE})")
        print("-"*35)

        if CH341DLL.CH341OpenDevice(c_uint(i_index)) > 0:

            if not CH341DLL.CH341SetExclusive(c_uint(i_index), c_uint(1)):
                raise RuntimeError("CH341SetExclusive")

            CH341ChipVer = CH341DLL.CH341GetVerIC(c_uint(i_index))
            CH341SPIBit = False

            if CH341ChipVer >= 48:
                CH341SPIBit = True

                CH341.setStream(i_index, 129)
                CH341.setD5D0(i_index, 63, 0)
                CH341.setDelaymS(i_index, 4)

                # ptr = CH341DLL.CH341GetDeviceName(c_ulong(i_index))
                # device_name = cast(ptr, c_char_p).value
                # print("Dev Name: ", device_name.decode('utf-8'))

                print(f"DLL Version: {CH341DLL.CH341GetVersion()}")
                print(f"Driver Version: {CH341DLL.CH341GetDrvVersion()}")
                self.read_spi_chip_id_341()

                t_start = time.time_ns()
                self.read_page(0, 10, None, False)
                t_end = time.time_ns()
                elapsed_time_ns = t_end - t_start
                self.page_time_ms = (elapsed_time_ns / 1e6)/10
                print(f"Page time: {self.page_time_ms:.1f} ms")

                print("-"*35)
                
            return True
        else:
            raise RuntimeError("Failed to open the device.")

    def close(self):
        print("-"*35)
        CH341DLL.CH341CloseDevice(c_uint(0))
        print("Device disconnected")

    """
    CH341StreamSPI4
    The parameter iChipSelect should be set to 0 if CS is not used. 
    Otherwise 0x80 if D0 is CS, 0x81 for D1 or 0x82 for D2.
    
    CH341SetStream
    Setting bit 2 of iMode to 1 enables the second SPI port. 
    D3 remains the common clock source, but D4 and D6 are additional data I/O lines. 
    If your hardware is MiniProgrammer, D4 and D6 are not connected to anything. 
    Bit 7 configures endianness. 
    Basically, for the MiniProgrammer this is the only bit you have to configure, therefore iMode can be 0x80 or 0x00.
    """

        
device = Device(BLOCKS_COUNT=1024)
device.open(0, spi_io=SPI_IO_DOUBLE)

MemSize = 134217728

# device.start_spi_mode_25()
# device.read_spi_chip_id_341()
# device.unlock_spi_chip_25()


device.read_flash_bytes()

# device.write_page(0, 'out.bin')
# device.read_page(0, 2, None)

# device.start_spi_mode_25()
# device.read_bytes(0, 1024*128, True, 'zloader')
# device.read_bytes(1024*128, 1024*1024, True, 'uboot')
# device.read_bytes(1024*128 + 1024*1024, 1024*1024, True, 'uboot_mirr')

# device.write_bytes(1024*128, 'uboot')

# data = device.read_page(0, 1, None)
# print(data, len(data))
device.close()
