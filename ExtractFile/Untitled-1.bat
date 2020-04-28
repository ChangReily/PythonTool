py -3 ExtractFile.py -i BIOS.bin -offset 0x000A6000 -size 0x99000 -o PSP_L1.bin
py -3 ExtractFile.py -i BIOS.bin -offset 0x0013F000 -size 0x20000 -o BIOS_L1.bin
py -3 ExtractFile.py -i BIOS.bin -offset 0x0015F000 -size 0x277000 -o PSP_L2.bin
py -3 ExtractFile.py -i BIOS.bin -offset 0x003D6000 -size 0x40000 -o BIOS_L2.bin
