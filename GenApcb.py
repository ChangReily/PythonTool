import os
import sys

argc = len(sys.argv)
ApcbZpD4FilePath=sys.argv[1]
ApcbZpD4DapFilePath=sys.argv[2]
HpApcbFileFilePath=sys.argv[3]


TempFilePtr = open ('Temp.bin',"wb")
Alignment=0x4000


#
# Write APCB_ZP_D4.bin
#
ApcbZpD4 = open (ApcbZpD4FilePath,"rb")
FileContent=ApcbZpD4.read()
TempFilePtr.write(FileContent)
ApcbZpD4Size = os.path.getsize(ApcbZpD4FilePath)
Count = Alignment - ApcbZpD4Size
while Count > 0:
    TempFilePtr.write(chr(0xFF))
    Count -=1
ApcbZpD4.close()


#
# Write APCB_ZP_D4_Dap.bin
#
ApcbZpD4Dap = open (ApcbZpD4DapFilePath,"rb")
FileContent=ApcbZpD4Dap.read()
TempFilePtr.write(FileContent)
ApcbZpD4DapSize = os.path.getsize(ApcbZpD4DapFilePath)
Count = Alignment - ApcbZpD4DapSize
while Count > 0:
    TempFilePtr.write(chr(0xFF))
    Count -=1
ApcbZpD4Dap.close()
TempFilePtr.close()


#
# Copy again for L1/L2
#
TempFilePtr = open ('Temp.bin',"rb")
FileContent=TempFilePtr.read()

HpApcbFile = open (HpApcbFileFilePath,"wb")
HpApcbFile.write(FileContent)
HpApcbFile.write(FileContent)

TempFilePtr.close()
HpApcbFile.close()

