import os
import subprocess


cmd='BiosConfigUtility64.exe /getconfig:"OldBiosConfigFile.txt"'
print (cmd)
Process = subprocess.call(cmd,shell=True )


OldFile = open("OldBiosConfigFile.txt", 'r')
NewFile= open("NewBiosConfigFile.txt",'w')
ProductNameFlag=False
SerialNumberFlag=False
SkuNumberFlag=False
SystemBoardCtNumberFlag=False
FeatureByteFlag=False
BuildIdFlag=False
FactoryMacAddFlag=False
SystemMacAddFlag=False

for line in OldFile.readlines():
    #
    # Product Name
    #
    if ProductNameFlag == True:
        ProductNameFlag=False
        line = '\tHP_Platform\n'
    if 'Product Name\n' == line:
        ProductNameFlag=True
    #
    # Serial Number
    #
    if SerialNumberFlag == True:
        SerialNumberFlag=False
        line = '\t123456789\n'
    if 'Serial Number\n' == line:
        SerialNumberFlag=True
             
    #
    # SKU Number
    #
    if SkuNumberFlag == True:
        SkuNumberFlag=False
        line = '\tTest\n'
    if 'SKU Number\n' == line:
        SkuNumberFlag=True

    #
    # System Board CT Number
    #
    if SystemBoardCtNumberFlag == True:
        SystemBoardCtNumberFlag=False
        line = '\tTest\n'
    if 'System Board CT Number\n' == line:
        SystemBoardCtNumberFlag=True

    #
    # Feature Byte
    #
    if FeatureByteFlag == True:
        FeatureByteFlag=False
        line = '\tdq.ar\n'
    if 'Feature Byte\n' == line:
        FeatureByteFlag=True

    #
    # Build ID
    #
    if BuildIdFlag == True:
        BuildIdFlag=False
        line = '\tTest\n'
    if 'Build ID\n' == line:
        BuildIdFlag=True       
    #
    # Manufacturing Programming Mode
    #
    if '\t*Unlock\n' == line:
        line = '\tUnlock\n'
    if '\tLock\n' == line:
        line = '\t*Lock\n'
    #
    # HBMA Factory MAC Address
    #
    if FactoryMacAddFlag == True:
        FactoryMacAddFlag=False
        line = '\t12-34-56-78-90-12\n'
    if 'HBMA Factory MAC Address\n' == line:
        FactoryMacAddFlag=True 
    #
    # HBMA System MAC Address
    #
    if SystemMacAddFlag == True:
        SystemMacAddFlag=False
        line = '\t12-34-56-78-90-12\n'
    if 'HBMA System MAC Address\n' == line:
        SystemMacAddFlag=True 
        
    NewFile.write(line)

OldFile.close()
NewFile.close()



cmd='BiosConfigUtility64.exe /setconfig:"NewBiosConfigFile.txt"'
print (cmd)
Process = subprocess.call(cmd,shell=True )


os.remove("OldBiosConfigFile.txt")
os.remove("NewBiosConfigFile.txt")

os.system("pause")
