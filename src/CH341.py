import ctypes
from ctypes import *
CH341DLL = ctypes.WinDLL("CH341")

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


    # # CH341GetInput
    # CH341DLL.CH341GetInput.argtypes = [c_uint, POINTER(c_ulong)]
    # CH341DLL.CH341GetInput.restype = c_bool

    # # CH341SetOutput
    # CH341DLL.CH341SetOutput.argtypes = [c_uint, c_uint, c_uint, c_uint]
    # CH341DLL.CH341SetOutput.restype = c_bool

    # # CH341Set_D5_D0
    # CH341DLL.CH341Set_D5_D0.argtypes = [c_uint, c_uint, c_uint]
    # CH341DLL.CH341Set_D5_D0.restype = c_bool

    # # CH341StreamSPI3
    # CH341DLL.CH341StreamSPI3.argtypes = [c_uint, c_uint, c_uint, c_void_p]
    # CH341DLL.CH341StreamSPI3.restype = c_bool

    # # CH341StreamSPI4
    # CH341DLL.CH341StreamSPI4.argtypes = [c_uint, c_uint, c_uint, c_void_p]
    # CH341DLL.CH341StreamSPI4.restype = c_bool

    # # CH341StreamSPI5
    # CH341DLL.CH341StreamSPI5.argtypes = [c_uint, c_uint, c_uint, c_void_p, c_void_p]
    # CH341DLL.CH341StreamSPI5.restype = c_bool

    # # CH341BitStreamSPI
    # CH341DLL.CH341BitStreamSPI.argtypes = [c_uint, c_uint, c_void_p]
    # CH341DLL.CH341BitStreamSPI.restype = c_bool

    # # CH341MemReadAddr0
    # CH341DLL.CH341MemReadAddr0.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341MemReadAddr0.restype = c_bool

    # # CH341MemReadAddr1
    # CH341DLL.CH341MemReadAddr1.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341MemReadAddr1.restype = c_bool

    # # CH341MemWriteAddr0
    # CH341DLL.CH341MemWriteAddr0.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341MemWriteAddr0.restype = c_bool

    # # CH341MemWriteAddr1
    # CH341DLL.CH341MemWriteAddr1.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341MemWriteAddr1.restype = c_bool

    # # CH341SetExclusive
    # CH341DLL.CH341SetExclusive.argtypes = [c_uint, c_uint]
    # CH341DLL.CH341SetExclusive.restype = c_bool

    # # CH341SetTimeout
    # CH341DLL.CH341SetTimeout.argtypes = [c_uint, c_uint, c_uint]
    # CH341DLL.CH341SetTimeout.restype = c_bool

    # # CH341ReadData
    # CH341DLL.CH341ReadData.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341ReadData.restype = c_bool

    # # CH341WriteData
    # CH341DLL.CH341WriteData.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341WriteData.restype = c_bool

    # # CH341GetDeviceName
    # CH341DLL.CH341GetDeviceName.argtypes = [c_uint]
    # CH341DLL.CH341GetDeviceName.restype = c_void_p

    # # CH341GetVerIC
    # CH341DLL.CH341GetVerIC.argtypes = [c_uint]
    # CH341DLL.CH341GetVerIC.restype = c_uint

    # # CH341FlushBuffer
    # CH341DLL.CH341FlushBuffer.argtypes = [c_uint]
    # CH341DLL.CH341FlushBuffer.restype = c_bool

    # # CH341WriteRead
    # CH341DLL.CH341WriteRead.argtypes = [c_uint, c_uint, c_void_p, c_uint, c_uint, POINTER(c_ulong), c_void_p]
    # CH341DLL.CH341WriteRead.restype = c_bool

    # # CH341SetStream
    # CH341DLL.CH341SetStream.argtypes = [c_uint, c_uint]
    # CH341DLL.CH341SetStream.restype = c_bool

    # # CH341SetDelaymS
    # CH341DLL.CH341SetDelaymS.argtypes = [c_uint, c_uint]
    # CH341DLL.CH341SetDelaymS.restype = c_bool

    # # CH341ReadInter
    # CH341DLL.CH341ReadInter.argtypes = [c_uint, POINTER(c_ulong)]
    # CH341DLL.CH341ReadInter.restype = c_bool

    # # CH341AbortInter
    # CH341DLL.CH341AbortInter.argtypes = [c_uint]
    # CH341DLL.CH341AbortInter.restype = c_bool

    # # CH341SetParaMode
    # CH341DLL.CH341SetParaMode.argtypes = [c_uint, c_uint]
    # CH341DLL.CH341SetParaMode.restype = c_bool

    # # CH341InitParallel
    # CH341DLL.CH341InitParallel.argtypes = [c_uint, c_uint]
    # CH341DLL.CH341InitParallel.restype = c_bool

    # # CH341ReadData0
    # CH341DLL.CH341ReadData0.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341ReadData0.restype = c_bool

    # # CH341ReadData1
    # CH341DLL.CH341ReadData1.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341ReadData1.restype = c_bool

    # # CH341AbortRead
    # CH341DLL.CH341AbortRead.argtypes = [c_uint]
    # CH341DLL.CH341AbortRead.restype = c_bool

    # # CH341WriteData0
    # CH341DLL.CH341WriteData0.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341WriteData0.restype = c_bool

    # # CH341WriteData1
    # CH341DLL.CH341WriteData1.argtypes = [c_uint, c_void_p, POINTER(c_ulong)]
    # CH341DLL.CH341WriteData1.restype = c_bool

    # # CH341AbortWrite
    # CH341DLL.CH341AbortWrite.argtypes = [c_uint]
    # CH341DLL.CH341AbortWrite.restype = c_bool

    # # CH341GetStatus
    # CH341DLL.CH341GetStatus.argtypes = [c_uint, POINTER(c_ulong)]
    # CH341DLL.CH341GetStatus.restype = c_bool

    # # CH341ResetDevice
    # CH341DLL.CH341ResetDevice.argtypes = [ctypes.c_uint]
    # CH341DLL.CH341ResetDevice.restype = ctypes.c_bool

    @staticmethod
    def setStream(iIndex:int, iMode:int) -> None:
        """
        BOOL WINAPI CH341SetStream( // Set the serial port stream mode
        ULONG iIndex,           // Specify CH341 device serial number
        ULONG iMode );          // Specify mode

        Mode:
         Bit 1-0: I2C interface speed/SCL frequency
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
    def setD5D0(iIndex:int, iSetDirOut:int, iSetDataOut:int) -> None:
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