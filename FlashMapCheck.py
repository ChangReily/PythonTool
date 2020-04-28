import re

FlashMap_File='FlashMap_16M.fdf'

if __name__ == "__main__":
    file=open(FlashMap_File, 'r')
    filebuffer=file.readlines()
    file.close()
    Counter=len(filebuffer)
    FlashBuffer=''
    SumSize=0
    for idx in range(0, Counter, 1):
        # if filebuffer[idx][0]=='#':
        #     continue
        # if 'OFFSET' in filebuffer[idx]:
        #     continue
        # if filebuffer[idx][0]=='\n':
        #     continue
        if 'FLASH_SIZE' in filebuffer[idx]:
            if filebuffer[idx][0]!='#':
                match=re.search('0x[0-9A-F]+', filebuffer[idx])
                FlashTotalSize=int(match.group(), 16)
                # print (f'{filebuffer[idx].rstrip()}  # 0x{FlashTotalSize:08X}')
        if 'REGION' in filebuffer[idx]:
            if 'OFFSET' not in filebuffer[idx]:
                LineBuffer=filebuffer[idx].strip()
                if LineBuffer[0]!='#':
                    match=re.search('0x[0-9A-F]+', filebuffer[idx])
                    if match != None:
                        Value=int(match.group(), 16)
                        Index=filebuffer[idx].find(match.group())
                        Index=Index+len(match.group())
                        StartOffset=SumSize
                        SumSize=SumSize+Value
                        # print (f'{filebuffer[idx][:Index]}  # 0x{StartOffset:08X} - 0x{SumSize:08X}')
                        filebuffer[idx]=f'{filebuffer[idx][:Index]}  # 0x{StartOffset:08X} - 0x{SumSize:08X}\n'

        FlashBuffer=FlashBuffer+filebuffer[idx]

    if FlashTotalSize != SumSize:
        print ('!!!!!!!!!!  ERROR !!!!!!!!!!')
        print (f'FLASH_SIZE = 0x{FlashTotalSize:08X}')
        print (f'Total Size = 0x{SumSize:08X}')
    else:
        # print (FlashBuffer)
        file=open(FlashMap_File, 'w')
        file.write(FlashBuffer)
        file.close()