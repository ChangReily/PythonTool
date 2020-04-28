import os
import subprocess
import sys
import re
import shutil
import time
import datetime

###############################################################################
# Project Configuration form ini file
###############################################################################
ProjectUrl=''
BiosIdPath=''
BiosVersion=''
BuildId=''

###############################################################################
# Global variable
###############################################################################
ProductionReleaseUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/branches/StagingCF'
TestReleaseUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/branches/Release'
ProductionUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/ProductionRelease/tags'
TestReleaseTagUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/TestRelease/tags'
ProjectName=''
Version=''
FamilyId=''
ReleaseType=''
PrepareStagingUrl=''
ProjtectRevision=''
CoreRevision=''
TempWorkspace=os.path.join(os.getcwd(), 'SvnTempFolder')
ExternalsFile=os.path.join(os.getcwd(), 'Externals.txt')
MessageFile=os.path.join(os.getcwd(), 'Message.txt')
MessageBuffer=''

###############################################################################
# subprocess call function
###############################################################################
def CallSubprocess(Cmd):
    Process=subprocess.Popen(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Processouts, Processerrs = Process.communicate()
    if Processouts != None:
        Buffer = Processouts.decode('UTF-8','ignore')
        print (Buffer)
    if Processerrs != None:
        Buffer = Processerrs.decode('UTF-8','ignore')
        print (Buffer)
    if Process.returncode != 0:
        print (f'ERROR to execute: {Cmd}')
        # sys.exit(1)
        raise ValueError('Execute command ERROR!!')
        
    return Process.returncode

###############################################################################
# Get Last Change version function
###############################################################################
def GetRevision(url: str) -> str:
    #print (url)
    process=subprocess.Popen(['svn', 'info', url], shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Revision=''
    for line in process.stdout:
        line = line.rstrip().decode('UTF-8','ignore')
        if line != '':
            match = re.search(r'^Last Changed Rev: (.*)', line)
            if match:
                Revision = match.group(1)
                #print (Revision)
    if Revision is '':
        print ('Unable to extract Project to get version!')
        # sys.exit(1)
        raise ValueError('Unable to extract Project')
    return Revision

###############################################################################
# Parsing INI file for Project information'
###############################################################################
def ParsingIniFile():
    global ProjectUrl
    global ProductionReleaseUrl
    global BiosVersion
    global BiosIdPath
    global BuildId
    global FamilyId
    global ReleaseType
    global ProjectName
    global Version
    global PrepareStagingUrl

    Argc = len(sys.argv )
    if Argc != 2: 
        print ("The command should follow below format:" )
        print ('')
        print (os.path.basename (sys.argv[0]) + " [ConfigFile.ini]")
        print ('')
        os.system("pause")
        sys.exit (1)    
    
    print (f'\n===== Parsing {os.path.basename (sys.argv[1])} config file =====')
    File=open(sys.argv[1],'r')
    Buffer=File.readlines()
    for line in Buffer:
        if '#' in line:
            continue
        if 'ReleaseType' in line:
            ReleaseType=line.split('=')[1].strip()
            print (f'ReleaseType : {ReleaseType}')
        if 'ProjectUrl' in line:
            ProjectUrl=line.split('=')[1].strip()
            print (f'ProjectUrl : {ProjectUrl}')
        if 'BiosIdPath' in line:
            BiosIdPath=line.split('=')[1].strip()
            if '\\' in BiosIdPath:
                BiosIdPath=BiosIdPath.replace('\\','/')
            print (f'BiosIdPath : {BiosIdPath}')
        if 'BiosVersion' in line:
            BiosVersion=line.split('=')[1].strip()
            print (f'BiosVersion: {BiosVersion}')
        if 'BuildId' in line:
            BuildId=line.split('=')[1].strip()
            print (f'BuildId    : {BuildId}')
    
    if ReleaseType is '':
        print ('\nERROR: ReleaseType is not defined!\n')
        # sys.exit(1)
        raise ValueError('ReleaseType is not defined!')
    else:
        if (ReleaseType != 'ProductionRelease') and (ReleaseType != 'TestRelease') and (ReleaseType != 'ProductionReleaseSMIP'):
            print ('\nERROR: ReleaseType should be "ProductionRelease" or "TestRelease"!\n')
            raise ValueError('ReleaseType is not defined!')
    
    if ProjectUrl is '':
        print ('\nERROR: ProjectUrl is not defined!\n')
        # sys.exit(1)
        raise ValueError('ProjectUrl is not defined!')
    if BiosIdPath is '':
        print ('\nERROR: BiosIdPath is not defined!\n')
        # sys.exit(1)
        raise ValueError('BiosIdPath is not defined!')
    if BiosVersion is '':
        print ('\nERROR: BiosVersion is not defined!\n')
        raise ValueError('BiosVersion is not defined!')
    if BuildId is '':
        print ('\nERROR: BuildId is not defined!\n')
        # sys.exit(1)
        raise ValueError('BuildId is not defined!')
    
    # Get Project Name
    if '@' in ProjectUrl:
        Version=ProjectUrl.rsplit('@',1)[1]
        ProjectUrl=ProjectUrl.rsplit('@',1)[0]
    ProjectName=ProjectUrl.rsplit('/',1)[1]

    # Convert Bios version to a list
    BiosVersionList=BiosVersion.split('.')

    # Get Family ID form BiosVersion.env
    Cmd=f'svn cat {ProjectUrl}/{BiosIdPath}'
    Process=subprocess.Popen(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Processouts, Processerrs = Process.communicate()
    if Processouts != None:
        Buffer=Processouts.decode('UTF-8','ignore').splitlines()
        for line in Buffer:
            line = line.rstrip()
            if 'BOARD_ID' in line:
                match=re.search(r'\b[A-Z][0-9A-Fa-f]{2}\b',line)
                if match:
                    FamilyId=match.group(0)
                else:
                    print (f'\nERROR: Can not find BOARD_ID in {BiosIdPath}\n')
                    raise ValueError(f'Can not find BOARD_ID in {BiosIdPath}')
    if Processerrs != None:
        Buffer = Processerrs.decode('UTF-8','ignore')
        print (Buffer)
    if Process.returncode != 0:
        raise ValueError(f'ERROR to get: {ProjectUrl}/{BiosIdPath}')
 
    if (ReleaseType == 'ProductionRelease'):
        # PrepareStagingUrl=f'{ProductionReleaseUrl}/{FamilyId[0]}_Family/{FamilyId}/{BiosVersionList[0]}{BiosVersionList[1]}{BiosVersionList[2]}_{BuildId}/{ProjectName}'
        PrepareStagingUrl=f'{ProductionReleaseUrl}/{FamilyId}/{BiosVersionList[0]}{BiosVersionList[1]}{BiosVersionList[2]}_{BuildId}/{ProjectName}'
    if (ReleaseType == 'ProductionReleaseSMIP'):
        # PrepareStagingUrl=f'{ProductionReleaseUrl}/{FamilyId[0]}_Family/{FamilyId}Smip/{BiosVersionList[0]}{BiosVersionList[1]}{BiosVersionList[2]}_{BuildId}/{ProjectName}'
        PrepareStagingUrl=f'{ProductionReleaseUrl}/{FamilyId}Smip/{BiosVersionList[0]}{BiosVersionList[1]}{BiosVersionList[2]}_{BuildId}/{ProjectName}'
    if (ReleaseType == 'TestRelease'):
        TodayYear=str(datetime.datetime.today().isocalendar()[0])
        WeekNum='%02d' % int(datetime.datetime.today().isocalendar()[1])
        PrepareStagingUrl=f'{TestReleaseUrl}/{TodayYear[2:]}ww{WeekNum}/{FamilyId}/{BiosVersionList[0]}{BiosVersionList[1]}{BiosVersionList[2]}_{BuildId}/{ProjectName}'
    print (f'Staging URL is as follows:')
    print (f'{PrepareStagingUrl}')
    return

###############################################################################
# Check the Bios version already used or not
###############################################################################
def CheckBiosVersionAlreadyUse():
    global ProductionUrl
    global BiosVersion

    print (f'\n===== Check BIOS version already used in release tag or not =====')
    # Convert Bios version to a list
    BiosVersionList=BiosVersion.split('.')
    if (int(BiosVersionList[0]) < 90 and int(BiosVersionList[0]) > 79) :
        print (f'\nERROR: Production version: {BiosVersion}')
        print ('\nProduction Feature Version Ranges are:')
        print ('(1 to 79) and (90 to 99)\n')
        raise ValueError(f'Production Feature Version is not correct!!')

    if (ReleaseType == 'ProductionRelease'):
        CheckProductionUrl=f'{ProductionUrl}/{FamilyId}/{BiosVersion}_{BuildId}'
    if (ReleaseType == 'ProductionReleaseSMIP'):
        CheckProductionUrl=f'{ProductionUrl}/{FamilyId}Smip/{BiosVersion}_{BuildId}'
    if (ReleaseType == 'TestRelease'):
        CheckProductionUrl=f'{TestReleaseTagUrl}/{FamilyId}/{BiosVersion}_{BuildId}'
    
    print (f'Check URL: {CheckProductionUrl}')
    SvnCmd=f'svn info {CheckProductionUrl}'
    Process=subprocess.Popen(SvnCmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Processouts, Processerrs = Process.communicate()
    if  Process.returncode != 0:    
        print (f'\nBIOS Version is not used.!!')
        Buffer = Processerrs.decode('UTF-8','ignore')
        # print ('----------')
        # print (Buffer)
        # print ('----------')
    else:
        print (f'\nERROR: BIOS Version is already used!!\n')
        Buffer = Processouts.decode('UTF-8','ignore')
        print ('----------')
        print (Buffer)
        print ('----------')
        raise ValueError(f'URL is already exist!!')
    return

###############################################################################
# Check the branch exist or not
###############################################################################
def CheckStagingUrlExist():
    global PrepareStagingUrl

    print (f'\n===== Check Staging URL is used or not=====')
    print (f'Check URL: {PrepareStagingUrl}')
    SvnCmd=f'svn info {PrepareStagingUrl}'
    Process=subprocess.Popen(SvnCmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Processouts, Processerrs = Process.communicate()
    if  Process.returncode != 0:    
        print (f'\nURL is not exist and prepare to create!!')
        # Buffer = Processerrs.decode('UTF-8','ignore')
        # print ('----------')
        # print (Buffer)
        # print ('----------')
    else:
        print (f'\nERROR: URL is already exist!!\n')
        Buffer = Processouts.decode('UTF-8','ignore')
        print ('----------')
        print (Buffer)
        print ('----------')
        raise ValueError(f'URL is already exist!!')
    return


###############################################################################
# Create branches/StagingCF
###############################################################################
def CreateStageBranch():
    global ProjectName
    global BiosVersion    
    global ProjectUrl
    global Version
    global PrepareStagingUrl

    if (ReleaseType == 'ProductionRelease'):
        ReleaseMessage='Production Release'
    if (ReleaseType == 'ProductionReleaseSMIP'):
        ReleaseMessage='SMIP Production Release'
    if (ReleaseType == 'TestRelease'):
        ReleaseMessage='Test Release'

    if Version == '':
        SvnCmd=f'svn copy -m "Prepare {ProjectName} {BiosVersion} signing for {ReleaseMessage}" --parents {ProjectUrl} {PrepareStagingUrl}'
    else:
        SvnCmd=f'svn copy -m "Prepare {ProjectName} {BiosVersion} signing for {ReleaseMessage}" --parents {ProjectUrl}@{Version} {PrepareStagingUrl}'
    print (f'\n===== Create branches to StageCF =====')
    print (SvnCmd)
    CallSubprocess(SvnCmd)
    return

###############################################################################
# Checkout the NewStaginCF URL to Temp foler; perpare to change PEG number 
# and BIOS version/Build ID
###############################################################################
def CheckoutPrepareStagingUrl():
    global PrepareStagingUrl
    global TempWorkspace
    global BiosIdPath

    print (f'\n===== Checkout StageCF =====')
    SvnCmd=f'svn checkout {PrepareStagingUrl} --depth empty {TempWorkspace}'
    print (SvnCmd)
    CallSubprocess(SvnCmd)

    BiosIdPathList=BiosIdPath.split('/')
    TempPath=''
    for idx in range(0, len(BiosIdPathList), 1):
        TempPath=TempPath+f'\\{BiosIdPathList[idx]}'
        SvnCmd=f'svn update --set-depth empty {TempWorkspace}{TempPath}'
        print (SvnCmd)
        CallSubprocess(SvnCmd)

    return

###############################################################################
# Update PEG number with external links
###############################################################################
def UpdateExternal():
    global ProjtectRevision
    global CoreRevision
    global TempWorkspace
    global MessageBuffer

    print (f'\n===== Update External PEG Number =====')

    #
    # Get svn/svn-psgfw-platform14 Repository Root
    #
    Cmd=f'svn info {TempWorkspace}'
    # print (Cmd)
    process=subprocess.Popen(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    PlatformSvnRootUrl=''
    for line in process.stdout:
        line = line.rstrip().decode('UTF-8','ignore')
        if line != '':
            match = re.search(r'^Repository Root: (.*)', line)
            if match:
                PlatformSvnRootUrl = match.group(1)
    if PlatformSvnRootUrl is '':
        print ('\nERROR: Unable to extract Project!\n')
        raise ValueError('Unable to extract Project')

    #print(f'Platform SVN Root Url: {PlatformSvnRootUrl}')

    #
    # Get SVN server location
    #
    SvnServerUrl=''
    SvnServerUrl=PlatformSvnRootUrl.rsplit('/',2)[0]
    #print(f'SVN Server URL       : {SvnServerUrl}')

    #
    # Get external links form Project to get HpCore path
    #
    Cmd=f'svn propget svn:externals {TempWorkspace}'
    print (Cmd)
    process=subprocess.Popen(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    HpCoreLink=''
    for line in process.stdout:
        line = line.rstrip().decode('UTF-8','ignore')
        regex = re.search('HpCore', line)
        if regex != None:
            HpCoreLink=line.split(' ')[0]
            #print(HpCoreLink)
            break
    HpCoreLink=SvnServerUrl+HpCoreLink
    #print(f'Core URL       : {HpCoreLink}')

    #
    # Get Revision for HpCoreUrl and ProjectUrl
    #
    ProjtectRevision=GetRevision(ProjectUrl)
    print(f'Platform: {ProjtectRevision}   {ProjectUrl} ')
    
    CoreRevision=GetRevision(HpCoreLink)
    print(f'Core    : {CoreRevision}    {HpCoreLink} ')

    print ('')

    
    SvnCmd=f'svn propget svn:externals {TempWorkspace}'
    print (SvnCmd)
    process=subprocess.Popen(SvnCmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    Buffer=''
    NeedUpdate=False
    for line in process.stdout:
        line = line.rstrip().decode('UTF-8','ignore')
        if '/svn/svn-psgfw-core' in line:
            if not 'ReleaseTags' in line:
                print('Invalid Core External:' + line,end="")
            line=line.split(' ')
            if '@' in line[0]:
                print (line[0])
            else:
                NeedUpdate=True
                print(line[0]+'@'+CoreRevision+' '+line[1])
                Buffer=Buffer+(line[0]+'@'+CoreRevision+' '+line[1])+'\n'
        elif '/svn/svn-psgfw-platform14' in line:
            line=line.split(' ')
            if '@' in line[0]:
                print (line[0])
            else:
                NeedUpdate=True
                print(line[0]+'@'+ProjtectRevision+' '+line[1])
                Buffer=Buffer+(line[0]+'@'+ProjtectRevision+' '+line[1])+'\n'
    f=open(ExternalsFile,'w')
    f.write(Buffer)
    f.close()

    if NeedUpdate == False:
        print (f'/nExternals does not update!')
    else:
        SvnCmd=f'svn propset svn:externals {TempWorkspace} -F {ExternalsFile}'
        print (SvnCmd)
        CallSubprocess(SvnCmd)

        MessageBuffer=MessageBuffer+f'Update PEG number\n'
        MessageBuffer=MessageBuffer+f'   Platform: {ProjtectRevision}\n'
        MessageBuffer=MessageBuffer+f'   Core    : {CoreRevision}'
    return

###############################################################################
# Update BIOS version/Build ID
###############################################################################
def UpdateBiosId():
    global TempWorkspace
    global MessageBuffer
    global BiosIdPath

    print (f'\n===== Update BIOS Version/Build ID ({BiosIdPath})=====')

    BiosIdPathTemp=BiosIdPath.replace('/','\\')
    f=open(os.path.join(TempWorkspace,BiosIdPathTemp),'r')
    contents=f.readlines()
    f.close()

    BiosVersionList=BiosVersion.split('.')
    OldBiosVersionList=[00,00,00]
    OldBuildId=0000
    Buffer=''
    NeedUpdate=False
    for line in contents:
        if 'VERSION_MAJOR' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{2}\b',line)
            if match:
                OldBiosVersionList[1]='%02d' % int(match.group(0),16)
                # print (OldBiosVersionList[1])
            line ='VERSION_MAJOR     = '+ ('%02X' % int(BiosVersionList[1]))+'\n'
        if 'VERSION_MINOR' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{2}\b',line)
            if match:
                OldBiosVersionList[2]='%02d' % int(match.group(0),16)
                # print (OldBiosVersionList[2])
            line ='VERSION_MINOR     = '+ ('%02X' % int(BiosVersionList[2]))+'\n'
        if 'VERSION_FEATURE' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{2}\b',line)
            if match:
                OldBiosVersionList[0]='%02d' % int(match.group(0),16)
                # print (OldBiosVersionList[0])
            line ='VERSION_FEATURE   = '+ ('%02X' % int(BiosVersionList[0]))+'\n'
        if 'BUILD_ID' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{4}\b',line)
            if match:
                OldBuildId='%04d' % int(match.group(0))
            line ='BUILD_ID          = '+ ('%04d' % int(BuildId))+'\n'
        Buffer=Buffer+line

    for idx in range(0, len(OldBiosVersionList), 1):
        # print (f'Old: {OldBiosVersionList[idx]}, New: {int(BiosVersionList[idx])}')
        if int(OldBiosVersionList[idx]) != int(BiosVersionList[idx]):
            # print (f'NeedUpdate: {NeedUpdate}')
            NeedUpdate=True

    if int(OldBuildId) != int(BuildId):
        # print (f'NeedUpdate: {NeedUpdate}')
        NeedUpdate=True

    if NeedUpdate == False:
        print (f'BiosId.env no need to update!')
    else:
        print (Buffer)
        f=open(TempWorkspace+'\\HpPlatformPkg\\BLD\\BiosId.env','w')
        f.write(Buffer)
        f.close()

        MessageBuffer=MessageBuffer+f'\nUpdate BiosId.env\n'
        MessageBuffer=MessageBuffer+f'   Version : {BiosVersion}\n'
        MessageBuffer=MessageBuffer+f'   Build ID: {BuildId}'

    return

###############################################################################
# Commit PEG number and BIOS version/Build ID
###############################################################################
def CommitPegAndBiosId():
    global ProjtectRevision
    global CoreRevision
    global TempWorkspace
    global MessageBuffer

    if not (MessageBuffer ==''):
        print (f'\n===== Commit External and BiosId.env change =====')

        print ('** Commit Message Start **')
        print (MessageBuffer)
        print ('** Commit Message End **')
        File=open(MessageFile, 'w')
        File.write(MessageBuffer)
        File.close()
        print ('')
        SvnCmd=f'svn commit -F {MessageFile} {TempWorkspace}'
        print (SvnCmd)
        CallSubprocess(SvnCmd)

    return

###############################################################################
# Main function
###############################################################################
if __name__ == '__main__':
    ParsingIniFile()
    CheckBiosVersionAlreadyUse()
    CheckStagingUrlExist()
    CreateStageBranch()
    CheckoutPrepareStagingUrl()
    UpdateExternal()
    UpdateBiosId()
    CommitPegAndBiosId()
    if (os.path.exists(MessageFile)):
        os.remove(MessageFile)
    if (os.path.exists(ExternalsFile)):
        os.remove(ExternalsFile)
    if (os.path.exists(TempWorkspace)):
        time.sleep(5)
        os.system('rd /S /Q "{}"'.format(TempWorkspace))

    print (f'\n===== Staging URL Create Done =====')
    print ('------------------------------------------------------------------------')
    SvnCmd=f'svn info {PrepareStagingUrl}'
    CallSubprocess(SvnCmd)
    SvnCmd=f'svn log -v -l 2 {PrepareStagingUrl}'
    CallSubprocess(SvnCmd)
    # print ('----------')
    print (f'\nPlease checkout the code with follow staging URL!!\n')
    print (f'{PrepareStagingUrl}')
    
    print (f'\nBefore send the signing request, please verify local build status!!\n')
    os.system("pause")
