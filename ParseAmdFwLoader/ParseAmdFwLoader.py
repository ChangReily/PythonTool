import configparser
import struct
import argparse
import re

EmbeddedFwStructList=[
#   [Offset, Len, Description]
    ['0x00', 4, 'Signature of Embedded Firmware Structure(0x55AA55AA)'],
    ['0x14', 4, 'Point directly to PSP Directory table start from Family 17h Models 00h-0Fh, or point to PSP combo Directory header.'],
    ['0x18', 4, 'Point to BIOS Directory table for Family 17h Models 00h-0Fh.'],
    ['0x1C', 4, 'Point to BIOS Directory table for Family 17h Models 10h-1Fh'],
    ['0x20', 4, 'Point to BIOS Directory table for Family 17h Models 30h-3Fh'],
    ['0x24', 4, 'Bit 0 Second_gen_efs.\nIf 1 this is a first-generation EFS structure that will be ignored by PSP boot ROM starting with Family 17h models 30h-3Fh.\nIf 0 then this is a second generation EFS structure'],
    ['0x30', 4, 'Point to promontory firmware'],
    ['0x34', 4, 'Point to low power promontory firmware'],
    ['0x40', 1, 'SpiReadMode for AMD Family 15h Models 60h-6Fh (update by AGESA-FCH)\n000b Normal read (up to 33M)\n001b Reserved\n010b Dual IO (1-1-2)\n011b Quad IO (1-1-4)\n100b Dual IO (1-2-2)\n101b Quad IO (1-4-4)\n110b Normal read (up to 66M)\n111b Fast Read'],
    ['0x41', 1, 'FastSpeedNew for Family 15h Models 60h-6Fh Value Description:\n0000b 66.66MHz.\n0001b 33.33MHz.\n0010b 22.22MHz.\n0011b 16.66MHz.\n0100b 100MHz.\n0101b 800KHz'],
    ['0x42', 1, 'Reserved'],
    ['0x43', 1, 'SpiReadMode for Family 17h Models 00h-0Fh,10h-1Fh (update by AGESA-FCH) Value Description:\n000b Normal read (up to 33M)\n001b Reserved\n010b Dual IO (1-1-2)\n011b Quad IO (1-1-4)\n100b Dual IO (1-2-2)\n101b Quad IO (1-4-4)\n110b Normal read (up to 66M)\n111b Fast Read'],
    ['0x44', 1, 'FastSpeedNew for Family 17h Models 00h-0Fh,10h-1Fh Value Description:\n0000b 66.66MHz.\n0001b 33.33MHz.\n0010b 22.22MHz.\n0011b 16.66MHz.\n0100b 100MHz.\n0101b 800kHz'],
    ['0x45', 1, 'QPR_Dummy Cycle configure for Family 17h Models 00h-0Fh, 10h-1Fh.'],
    ['0x46', 1, 'Reserved'],
    ['0x47', 1, '(ReadOnly) SpiReadMode for Family 17h Models 30h-3Fh and later Families \nif (SpiReadMode==2,3,4,5,6,7) {\n  set spimode\n} else {\n  do nothing\n}\nValue Description:\n000b Normal read (up to 33M)\n001b Reserved\n010b Dual IO (1-1-2)\n011b Quad IO (1-1-4)\n100b Dual IO (1-2-2)\n101b Quad IO (1-4-4)\n110b Normal read (up to 66M)\n111b Fast Read'],
    ['0x48', 1, '(ReadOnly) SpiFastSpeed for Family 17h Models 30h-3Fh and later Families\nif (SpiReadMode==0,1,2,3,4,5) {\n  set SpiFastSpeed\n} else {\n  do nothing\n}\nValue Description:\n0000b 66.66MHz.\n0001b 33.33MHz.\n0010b 22.22MHz.\n0011b 16.66MHz.\n0100b 100MHz.\n0101b 800KHz.'],
    ['0x49', 1, '(ReadOnly) MicronDetectFlag for Family 17h Models 30h-3Fh and later Families\nif (MicronDetectFlag==0x55){ \n  if (PSP detect Micron VendorID = =0x20) {\n    DPR_DUMMYCYCLE = 0x8;\n    QPR_DUMMYCYCLE = 0xA;\n  }\n} else if (MicronDetectFlag==0xAA) {\n   DPR_DUMMYCYCLE = 0x8;\n   QPR_DUMMYCYCLE = 0xA;\n} else {\n  do nothing\n}\nValue Description:\n0x55:force Micron detection, if the bios supports Micron and non Micron.\n0xAA:force Micron dummycycle, if the bios supports Micron only\nothers: do nothing, if the board does NOT support Micron'],
    ['0x4A', 1, 'Reserved']
]
def CoverIniToInc(InputFile, OutFile):
    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(InputFile)
    List=[]
    for idx in range(0, len(EmbeddedFwStructList), 1):
        SubList=[]
        SubList.append(EmbeddedFwStructList[idx][0])
        Item = config.items(EmbeddedFwStructList[idx][0])
        # print (Item[0][0])
        HexStr=Item[0][0][2:]
        # IntValue=int(Item[0][0], 0)
        # HexStr=format(IntValue, 'x')
        # print (HexStr)
        HexStr_bytes = bytes.fromhex(HexStr)
        if EmbeddedFwStructList[idx][1] == 1:
            FormatCharacters='B'
            Value=struct.unpack(FormatCharacters, HexStr_bytes)
            # print (f'{EmbeddedFwStructList[idx][0]}: 0x{Value[0]:02X}')
            ValueStr=f'0x{Value[0]:02X}'
            
        if EmbeddedFwStructList[idx][1] == 4:
            FormatCharacters='BBBB'
            Value=struct.unpack(FormatCharacters, HexStr_bytes)
            # print (f'{EmbeddedFwStructList[idx][0]}: 0x{Value[3]:02X}, 0x{Value[2]:02X}, 0x{Value[1]:02X}, 0x{Value[0]:02X}')
            ValueStr=f'0x{Value[3]:02X}, 0x{Value[2]:02X}, 0x{Value[1]:02X}, 0x{Value[0]:02X}'
        SubList.append(EmbeddedFwStructList[idx][1])
        SubList.append(ValueStr)
        List.append(SubList)

    # print (List)

    Buffer='#pragma once\n\n#define DATA \\\n  '

    for idx in range(0, int('0x40',0), 4):
        for idx2 in range(0, len(List), 1):
            if idx == int(List[idx2][0], 0):
                ValueStr=List[idx2][2]+', '
                break
            if idx <= int('0x20',0):
                ValueStr='0x00, 0x00, 0x00, 0x00, '
            else:
                ValueStr='0xFF, 0xFF, 0xFF, 0xFF, '
        # print (f'{idx:02X} - {ValueStr}')
        Buffer=Buffer+ValueStr

    for idx in range(int('0x40',0), int('0x50',0), 1):
        for idx2 in range(0, len(List), 1):
            if idx == int(List[idx2][0], 0):
                ValueStr=List[idx2][2]+', '
                break
            else:
                ValueStr='0xFF, '
        # print (f'{idx:02X} - {ValueStr}')
        Buffer=Buffer+ValueStr

    Buffer=Buffer[0:-2]
    print (Buffer)

    f=open(OutFile,'w')
    f.write(Buffer)
    f.close()
    return

def ProcessIniBuffer(Offset, DataStr):
    ItemBuffer=''
    for idx in range(0, len(EmbeddedFwStructList), 1):
        if Offset==EmbeddedFwStructList[idx][0]:
            CommentBuffer=EmbeddedFwStructList[idx][2]
            # if '\n' in CommentBuffer:
            FoundCrlf=re.search('\\n',CommentBuffer)
            if FoundCrlf:
               CommentBuffer=re.sub('\\n', '\\n# ', CommentBuffer)
            ItemBuffer=f'# {Offset} - {CommentBuffer}\n'+f'[{Offset}]\n'+f'{DataStr}\n\n'
    return ItemBuffer

def CoverBinToIni(InputFile, OutFile):
    print ('Parsing Binary File to config ini file\n')
    Signature=b'\xAA\x55\xAA\x55'
    Found=-1
    with open(InputFile, 'rb') as f:
        s = f.read()
        Found=s.find(Signature)
    if Found == -1:
        print (f'Cant not found Embedded Firmware Structure Signature: 0x55AA55AA\n')
    else:
        print (f'The offset of Embedded Firmware Structure Signature: {hex(Found)}')
        BinBuffer=s[Found:Found+int('0x50',0)]
        HexString=BinBuffer.hex()
        # print (HexString)
        Buffer=''
        for idx in range(0, int('0x40',0)*2, 8):
            ValueStr=HexString[idx:idx+8]
            # print (ValueStr)
            ValueStr=bytes.fromhex(ValueStr)
            Value=struct.unpack('BBBB', ValueStr)
            Value4=f'0x{Value[3]:02X}{Value[2]:02X}{Value[1]:02X}{Value[0]:02X}'
            if idx > 0:
                idx=int(idx/2)
            
            Buffer=Buffer+ProcessIniBuffer(f'0x{idx:02X}', f'{Value4}')
            print (f'0x{idx:02X} - {Value4}')
                
        for idx in range(int('0x40',0)*2, int('0x50',0)*2, 2):
            ValueStr=HexString[idx:idx+2]
            # print (ValueStr)
            ValueStr=int(ValueStr, 16)
            idx=int(idx/2)
            Buffer=Buffer+ProcessIniBuffer(f'0x{idx:02X}', f'0x{ValueStr:02X}')
            print (f'0x{idx:02X} - {ValueStr:02X}')
        # print (Buffer)

        f=open(OutFile,'w')
        f.write(Buffer)
        f.close()    
    return

def CoverIncToIni(InputFile, OutFile):
    print ('Parsing inc File to config ini file\n')
    f=open(InputFile,'r')
    s = f.read()
    f.close()
    StrBuffer=re.sub('\\s+','', s)
    Found=StrBuffer.find('0xAA,0x55,0xAA,0x55')
    
    if Found == -1:
        print (f'Cant not found Embedded Firmware Structure Signature: 0x55AA55AA\n')
    else:
        StrBuffer=StrBuffer[Found:]
        StrBuffer=re.sub('0x','', StrBuffer)
        StrBuffer=re.sub(',','', StrBuffer)
        HexString=StrBuffer
        # print (HexString)
        Buffer=''
        for idx in range(0, int('0x40',0)*2, 8):
            ValueStr=HexString[idx:idx+8]
            # print (ValueStr)
            ValueStr=bytes.fromhex(ValueStr)
            Value=struct.unpack('BBBB', ValueStr)
            Value4=f'0x{Value[3]:02X}{Value[2]:02X}{Value[1]:02X}{Value[0]:02X}'
            if idx > 0:
                idx=int(idx/2)
            
            Buffer=Buffer+ProcessIniBuffer(f'0x{idx:02X}', f'{Value4}')
            print (f'0x{idx:02X} - {Value4}')
                
        for idx in range(int('0x40',0)*2, int('0x50',0)*2, 2):
            ValueStr=HexString[idx:idx+2]
            # print (ValueStr)
            ValueStr=int(ValueStr, 16)
            idx=int(idx/2)
            Buffer=Buffer+ProcessIniBuffer(f'0x{idx:02X}', f'0x{ValueStr:02X}')
            print (f'0x{idx:02X} - {ValueStr:02X}')
        # print (Buffer)

        f=open(OutFile,'w')
        f.write(Buffer)
        f.close()    
    
    return
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Covert AMD Embedded Firmware Structure.')
    parser.add_argument('-m','--mode', required=True, type=str, choices=['IniToInc', 'BinToIni', 'IncToIni'], help='Conver Mode ')
    parser.add_argument('-i','--input', required=True, type=str, help='Input file')
    parser.add_argument('-o','--output', required=True, type=str, help='Output file')
    args = parser.parse_args()
    # print (args.mode)
    # print (args.input)
    # print (args.output)
    print ('\nDesignd form #55758 AMD Platform Security Processor BIOS Architecture Design Guide for AMD Family 17h Processors\n')
    if (args.mode == 'IniToInc'):
        CoverIniToInc(args.input, args.output)
    if (args.mode == 'BinToIni'):
        CoverBinToIni(args.input, args.output)
    if (args.mode == 'IncToIni'):
        CoverIncToIni(args.input, args.output)
