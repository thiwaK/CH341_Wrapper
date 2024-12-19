# import ctypes
# from ctypes import *
import struct
from io import BytesIO, BufferedReader, SEEK_END, SEEK_SET
import time
import zlib

from src.CH341 import *



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

VENDOR_READ = 0xC0   # CH341 manufacturer-specific read operation implemented through control transmission
VENDOR_WRITE = 0x40  # CH341 manufacturer-specific write operation implemented through control transmission

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

class Error:

    DEV_NOT_OPEN = "Device not open. Try open_device first."

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


WT_PAGE = 0
WT_SSTB = 1
WT_SSTW = 2

class MEMORY_ID:
    def __init__(self):
        self.ID9FH = [0, 0, 0]
        self.ID90H = [0, 0]
        self.IDABH = 0
        self.ID15H = [0, 0]

class Device:
    
    def __init__(self, OOB_SIZE=64, PAGE_SIZE=2048+64, BLOCK_SIZE=135168, BLOCKS_COUNT=1024):

        self.PAGE_SIZE = PAGE_SIZE
        self.BLOCK_SIZE = BLOCK_SIZE
        self.PAGE_OOB_SIZE = OOB_SIZE

        self.PAGE_DATA_SIZE = PAGE_SIZE - OOB_SIZE
        self.PAGES_PER_BLOCK = int(BLOCK_SIZE/PAGE_SIZE)
        self.CHIP_SIZE = BLOCK_SIZE * BLOCKS_COUNT

        self.dev_open = False
        self.dev_index = 0

        self.util = Util()
        self.ID = MEMORY_ID()

    def spi_init(self):
        if not self.dev_open:
            raise RuntimeError(Error.DEV_NOT_OPEN)
        
        CH341.setStream(self.dev_index, 129)
        CH341.setD5D0(self.dev_index, 0x29, 0)

    def spi_deinit(self):
        if not self.dev_open:
            raise RuntimeError(Error.DEV_NOT_OPEN)
        CH341.setD5D0(self.dev_index, 0, 0)


    def spi_read(self, cs: int, buffer_len: int, buffer: list[int]) -> int:
        if not self.dev_open:
            raise RuntimeError(Error.DEV_NOT_OPEN)
        if cs == 1:
            if not CH341.streamSPI4(self.dev_index, 0x80, buffer_len, buffer):
                return -1
            return buffer_len
        else:
            CH341.setD5D0(self.dev_index, 0x29, 0)
            if CH341.streamSPI4(self.dev_index, 0, buffer_len, buffer):
                return -1
            return buffer_len

    def spi_write(self, cs: int, buffer_len: int, buffer: list[int]) -> int:
        if not self.dev_open:
            raise RuntimeError(Error.DEV_NOT_OPEN)
        if cs == 1:
            if not CH341.streamSPI4(self.dev_index, 128, buffer_len, buffer): #128=0x80
                return -1
            return buffer_len
        else:
            CH341.setD5D0(self.dev_index, 0x29, 0)  # Manually toggle CS
            if not CH341.streamSPI4(self.dev_index, 0, buffer_len, buffer):
                return -1
            return buffer_len


    def UsbAsp25_ReadID(self, ID):
        

        # 9F command
        buffer = create_string_buffer(4)
        buffer[0] = 0x9F
        
        self.SPIWrite(0, 1, buffer)
        buffer = bytearray([0xFF, 0xFF, 0xFF, 0xFF])
        pointer = cast(create_string_buffer(buffer), POINTER(ctypes.c_byte))
        self.SPIRead(1, 3, buffer)
        ID.ID9FH = buffer[:3]

        print(buffer)
        
        # 90 command
        buffer = bytes([0x90, 0, 0, 0])
        self.SPIWrite(0, 4, buffer)
        result = self.SPIRead(1, 2, buffer)
        ID.ID90H = buffer[:2]
        
        # AB command
        buffer = bytes([0, 0, 0, 0])
        buffer[0] = 0xAB
        SPIWrite(0, 4, buffer)
        result = SPIRead(1, 1, buffer)
        ID.IDABH = buffer[0]
        
        # 15 command
        buffer[0] = 0x15
        SPIWrite(0, 1, buffer)
        buffer = [0xFF, 0xFF]
        result = SPIRead(1, 2, buffer)
        ID.ID15H = buffer[:2]

    def UsbAsp25_ReadSR(self, sreg, opcode=0x05):
        self.SPIWrite(0, 1, bytes([opcode]))
        return self.SPIRead(1, 1, sreg)

    def __UsbAsp25_WriteSR__(self, sreg, opcode=0x01):
        buff = bytes([0x50])
        self.SPIWrite(1, 1, buff)
        buff = bytes([opcode, sreg])
        return self.SPIWrite(1, 2, buff)

    def __UsbAsp25_WriteSR_2byte__(self, sreg1, sreg2):
        buff = bytes([0x50])
        self.SPIWrite(1, 1, buff)
        buff = bytes([0x01, sreg1, sreg2])
        return self.SPIWrite(1, 3, buff)


    def UsbAsp25_Read32bitAddr(self, Opcode, Addr, buffer, bufflen):

        byte_1 = (Addr >> 24) & 0xFF  # Most significant byte
        byte_2 = (Addr >> 16) & 0xFF  # Second byte
        byte_3 = (Addr >> 8) & 0xFF   # Third byte
        byte_4 = Addr & 0xFF          # Least significant byte

        # byte_1 = (Addr >> 8) & 0xFF  # Most significant byte
        # byte_2 = (Addr >> 0xFF00) & 8  # Second byte
        # byte_3 = (Addr >> 0) & 0xFF   # Third byte
        # byte_4 = Addr & 0xFF          # Least significant byte
        
        print(f"Extracted bytes: {Opcode:02X} {byte_1:02X} {byte_2:02X} {byte_3:02X} {byte_4:02X}")
        addr_buffer = bytes([Opcode, byte_1, byte_2, byte_3, byte_4])

        self.SPIWrite(0, 5, addr_buffer)
        return self.SPIRead(1, bufflen, buffer)

    def UsbAsp25_Write32bitAddr(self, Opcode, Addr, buffer, bufflen):
        buff = bytes([
                    Opcode,
                    (Addr >> 24) & 0xFF,
                    (Addr >> 16) & 0xFF,
                    (Addr >> 8) & 0xFF,
                    Addr & 0xFF
                ])
        self.SPIWrite(0, 5, buff)
        return self.SPIWrite(1, bufflen, buffer)


    def UsbAsp25_Read(self, Opcode, Addr, buffer, bufflen):
        buff = bytes([Opcode, (Addr >> 8) & 0xFF, (Addr >> 16) & 0xFF, Addr & 0xFF])
        self.SPIWrite(0, 4, buff)
        x = self.SPIRead(1, bufflen, buffer)
        print(zlib.crc32(x))
        return x

    def UsbAsp25_Write(self, Opcode, Addr, buffer, bufflen):
        buff = bytes([Opcode, (Addr >> 8) & 0xFF, (Addr >> 16) & 0xFF, Addr & 0xFF])
        self.SPIWrite(0, 4, buff)
        return self.SPIWrite(1, bufflen, buffer)

    ###
    def UsbAsp25_Busy(self):
        sreg = bytes([255])
        self.UsbAsp25_ReadSR(sreg)
        return (int(sreg[0]) & 0x01) != 0


    def EnterProgMode25(self, spiSpeed, SendAB=False):
        
        self.spi_init()
        time.sleep(0.05)

        if SendAB:
            self.SPIWrite(1, 1, bytes([0xAB]))
        time.sleep(0.002)

    def ExitProgMode25(self):
        self.spi_deinit()


    def UsbAsp25_Wren(self):
        buff = bytes([0x06])
        return self.SPIWrite(1, 1, buff)

    def UsbAsp25_Wrdi(self):
        buff = bytes([0x04])
        return self.SPIWrite(1, 1, buff)

    def UsbAsp25_ChipErase(self):
        buff = bytes([0x62])
        self.SPIWrite(1, 1, buff)
        buff = bytes([0x60])
        self.SPIWrite(1, 1, buff)
        buff = bytes([0xC7])
        return self.SPIWrite(1, 1, buff)



    def UsbAsp25_WriteSSTB(self, Opcode, Data):
        buff = bytes([Opcode, Data])
        return self.SPIWrite(1, 2, buff) - 1

    def UsbAsp25_WriteSSTW(self, Opcode, Data1, Data2):
        buff = bytes([Opcode, Data1, Data2])
        return self.SPIWrite(1, 3, buff) - 1

    def UsbAsp25_EN4B(self):
        self.UsbAsp25_Wren()
        buff = bytes([0xB7])
        self.SPIWrite(1, 1, buff)
        
        # Access Spansion Bank Register
        buff = bytes([0x17])
        self.SPIWrite(0, 1, buff)
        buff = bytes([0x80]) # EXTADD=1
        return self.SPIWrite(1, 1, buff)

    def UsbAsp25_EX4B(self):
        self.UsbAsp25_Wren()
        buff = bytes([0xE9])
        return self.SPIWrite(1, 1, buff)


    def SPIRead(self, CS: int, BufferLen: int, buffer: bytes):
        if not self.dev_open:
            raise RuntimeError(Error.DEV_NOT_OPEN)

        # print("")
        # while self.UsbAsp25_Busy():
        #     time.sleep(0.1)
        #     print(".", end='')

        if(CS == 1):
            if not CH341.streamSPI4(self.dev_index, 0x80, BufferLen, buffer):
                print("FAILED")
                return -1 
            print("cs:1", zlib.crc32(buffer))
            return BufferLen
        else:
            CH341.setD5D0(self.dev_index, 0x29, 0)
            if not CH341.streamSPI4(self.dev_index, 0, BufferLen, buffer):
                print("FAILED")
                return -1
            print("cs:0", zlib.crc32(buffer))
            return BufferLen

    def SPIWrite(self, CS: int, BufferLen: int, buffer: bytes):
        if not self.dev_open:
            raise RuntimeError(Error.DEV_NOT_OPEN)

        if(CS == 1):
            if not CH341.streamSPI4(self.dev_index, 0x80, BufferLen, buffer):
                return -1 
            return BufferLen
        else:
            CH341.setD5D0(self.dev_index, 0x29, 0)
            if not CH341.streamSPI4(self.dev_index, 0, BufferLen, buffer):
                return -1 
            return BufferLen

    def IsLockBitsEnabled(self):
        result = False
        sreg = bytes([0])
        sreg2 = bytes([0])
        sreg3 = bytes([0])

        self.UsbAsp25_ReadSR(sreg); #Читаем регистр
        self.UsbAsp25_ReadSR(sreg2, 0x35); #Второй байт
        self.UsbAsp25_ReadSR(sreg3, 0x15); #Третий байт
        print(sreg, sreg2, sreg3)
        # print(f"Sreg: {bin(sreg)[2:].zfill(8)}(0x{hex(sreg)[2:].zfill(2)}), "
        #   f"{bin(sreg2)[2:].zfill(8)}(0x{hex(sreg2)[2:].zfill(2)}), "
        #   f"{bin(sreg3)[2:].zfill(8)}(0x{hex(sreg3)[2:].zfill(2)})")




        return result



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
        
        CH341.setD5D0(index, 0x29, 0)
        CH341.streamSPI4(index, 0, buffer_len, buffer)

        # print(self.byte_to_hex_string(buffer[0:10]), self.byte_to_hex_string(buffer[-10:]), zlib.crc32(buffer))


        if value == 1:
            CH341.setD5D0(self.dev_index, 0x29, 1)
        return buffer_len

    def write_spi_341(self, value, index, buffer_len, buffer):

        CH341.setD5D0(index, 0x29, 0)
        CH341.streamSPI4(index, 0, buffer_len, buffer)
        
        if value == 1:
            CH341.setD5D0(index, 0x29, 1)
        
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
        iPageSize = self.PAGE_DATA_SIZE
        iChipSize = self.CHIP_SIZE

        if start_page != None and end_page != None and end_page > 0:
            address = start_page * iPageSize
            iChipSize = end_page * iPageSize

        
        ms = BytesIO()


        if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
            self.UsbAsp25_EN4B()

        if verbouse:
            print(f"Reading from page {start_page} to {end_page}")
            print(f"Reading time: {self.util.format_time(self.page_time_ms*(end_page - start_page))}")

        while (address < iChipSize):

            time.sleep(0.1)

            buffer = bytes([0 for x in range(self.PAGE_SIZE)])
            
            if (iPageSize > iChipSize - address):
                iPageSize = iChipSize - address

            if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
                bytesRead += self.read_32bit_address_spi25_341(address, iPageSize, buffer)
                # bytesRead += self.UsbAsp25_Read32bitAddr(0x03, address, buffer, iPageSize)
            else:
                bytesRead += self.read_16bit_address_spi25_341(address, iPageSize, buffer);
            
            ms.write(buffer)
            address += iPageSize

            print(zlib.crc32(buffer))
            del buffer

            

        if (self.CHIP_SIZE > FLASH_SIZE_128BIT):
            self.UsbAsp25_EX4B()

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

        print(f"Start writing {iDataSize - address} bytes from address {address}")

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


    def open(self, i_index, spi_io=SPI_IO_SINGLE, spi_bit_order=SPI_BIT_ORDER_BIG):

        print("="*35)
        print(f"Chip size :", self.CHIP_SIZE, f"{int(self.CHIP_SIZE/1024/1024)}MBit")
        print(f"Block size:", self.BLOCK_SIZE, f"({self.PAGES_PER_BLOCK} pages)")
        print(f"Page size :", self.PAGE_SIZE, f"({self.PAGE_DATA_SIZE} + {self.PAGE_OOB_SIZE})")
        print("-"*35)

        if CH341DLL.CH341OpenDevice(i_index) != 0xFFFFFFFF:

            self.dev_open = True
            self.dev_index = i_index

            if not CH341DLL.CH341SetExclusive(c_uint(i_index), c_uint(0)): #0=shared 1=exclusive
                raise RuntimeError("CH341SetExclusive")

            CH341ChipVer = CH341DLL.CH341GetVerIC(c_uint(i_index))
            print(f"Chip Version: {CH341ChipVer}")

            CH341SPIBit = False

            if CH341ChipVer >= 48:
                CH341SPIBit = True

                self.spi_init()

                # CH341.setDelaymS(i_index, 4)

                # ptr = CH341DLL.CH341GetDeviceName(c_ulong(i_index))
                # device_name = cast(ptr, c_char_p).value
                # print("Dev Name: ", device_name.decode('utf-8'))
                #
                


                print(f"DLL Version: {CH341DLL.CH341GetVersion()}")
                print(f"Driver Version: {CH341DLL.CH341GetDrvVersion()}")
                print(f"Is locked: {self.IsLockBitsEnabled()}")
                time.sleep(0.1)

                self.UsbAsp25_ReadID(self.ID)
                print(self.ID)


                t_start = time.time_ns()
                self.read_page(0, 3, None, False)
                t_end = time.time_ns()
                elapsed_time_ns = t_end - t_start
                self.page_time_ms = (elapsed_time_ns / 1e6)/3
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
# time.sleep(1)
# print(device.UsbAsp25_Busy())
# MemSize = 134217728

# device.start_spi_mode_25()
# device.read_spi_chip_id_341()
# device.unlock_spi_chip_25()


# device.read_flash_bytes()

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

