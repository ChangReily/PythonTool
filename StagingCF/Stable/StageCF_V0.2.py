import os
import subprocess
import sys
import re
import shutil

###############################################################################
# Project Configuration form ini file
###############################################################################
ProjectUrl=''
StageCFUrl=''
BiosId=''
BuildId=''

###############################################################################
# Global variable
###############################################################################
ProjectName=''
NewStageCFUrl=''
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
        Buffer = Processouts.decode("utf-8")
        print (Buffer)
    if Processerrs != None:
        Buffer = Processerrs.decode("utf-8")
        print (Buffer)
    if Process.returncode != 0:
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
        raise ValueError('Unable to extract Project')
    return Revision

###############################################################################
# Parsing INI file for Project information'
###############################################################################
def ParsingIniFile():
    global ProjectUrl
    global StageCFUrl
    global BiosId
    global BuildId
    global ProjectName
    global NewStageCFUrl

    Argc = len(sys.argv )
    if Argc != 2: 
        print ("The command should follow below format:" )
        print ('')
        print ("   py -3 " + os.path.basename (sys.argv[0]) + " ConfigFile.ini")
        sys.exit (1)    
    
    print (f'\n===== Parsing {os.path.basename (sys.argv[1])} config file =====')
    File=open(sys.argv[1],'r')
    Buffer=File.readlines()
    for line in Buffer:
        if 'ProjectUrl' in line:
            ProjectUrl=line.split('=')[1].strip()
            print (f'ProjectUrl: {ProjectUrl}')
        if 'StageCFUrl' in line:
            StageCFUrl=line.split('=')[1].strip()
            print (f'StageCFUrl: {StageCFUrl}')
        if 'BiosId' in line:
            BiosId=line.split('=')[1].strip()
            print (f'BiosId    : {BiosId}')
        if 'BuildId' in line:
            BuildId=line.split('=')[1].strip()
            print (f'BuildId   : {BuildId}')
        
    ProjectName=ProjectUrl.rsplit('/',1)[1]
    BiosIdList=BiosId.split('.')
    NewStageCFUrl=f'{StageCFUrl}/{BiosIdList[0]}{BiosIdList[1]}{BiosIdList[2]}_{BuildId}/{ProjectName}'

    print (f'\nStaging URL is as follows:')
    print (f'{NewStageCFUrl}')
    return

###############################################################################
# Create branches/StagingCF/BiosXXplatform/'PlatformName'/'XXXXXX_XXXX'/'PlatformName'
# ex: branches/StagingCF/Bios17platform/HpBalos10/999999_0000/HpBalos
###############################################################################
def CreateStageBranch():
    global ProjectName
    global BiosId    
    global ProjectUrl
    global NewStageCFUrl

    SvnCopycmd=f'svn copy -m "Perpare {ProjectName} {BiosId} signing" --parents {ProjectUrl} {NewStageCFUrl}'
    print (f'\n===== Create branches to StageCF =====')
    print (f'{SvnCopycmd}')
    CallSubprocess(SvnCopycmd)
    return

###############################################################################
# Checkout the NewStaginCF URL to Temp foler; perpare to change PEG number 
# and BIOS version/Build ID
###############################################################################
def CheckoutNewStageCFUrl():
    global NewStageCFUrl
    global TempWorkspace
    print (f'\n===== Checkout StageCF =====')
    CheckoutCmd=f'svn checkout {NewStageCFUrl} --depth empty {TempWorkspace}'
    print (CheckoutCmd)
    CallSubprocess(CheckoutCmd)

    UpdateCmd=f'svn update --set-depth empty {TempWorkspace}\\HpPlatformPkg'
    print (UpdateCmd)
    CallSubprocess(UpdateCmd)
    UpdateCmd=f'svn update --set-depth empty {TempWorkspace}\\HpPlatformPkg\\BLD'
    print (UpdateCmd)
    CallSubprocess(UpdateCmd)
    UpdateCmd=f'svn update --set-depth empty {TempWorkspace}\\HpPlatformPkg\\BLD\\BiosId.env'
    print (UpdateCmd)
    CallSubprocess(UpdateCmd)
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
    process=subprocess.Popen(['svn', 'info', TempWorkspace], shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    PlatformSvnRootUrl=''
    for line in process.stdout:
        line = line.rstrip().decode('UTF-8','ignore')
        if line != '':
            match = re.search(r'^Repository Root: (.*)', line)
            if match:
                PlatformSvnRootUrl = match.group(1)
    if PlatformSvnRootUrl is '':
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
    HpCoreLink=''
    process=subprocess.Popen(['svn', 'propget', 'svn:externals', TempWorkspace], shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

    Buffer=''
    process=subprocess.Popen(['svn', 'propget', 'svn:externals', TempWorkspace], shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in process.stdout:
        line = line.rstrip().decode('UTF-8','ignore')
        if '/svn/svn-psgfw-core' in line:
            if not 'ReleaseTags' in line:
                print('Invalid Core External:' + line,end="")
            line=line.split(' ')
            print(line[0]+'@'+CoreRevision+' '+line[1])
            Buffer=Buffer+(line[0]+'@'+CoreRevision+' '+line[1])+'\n'
        elif '/svn/svn-psgfw-platform14' in line:
            line=line.split(' ')
            print(line[0]+'@'+ProjtectRevision+' '+line[1])
            Buffer=Buffer+(line[0]+'@'+ProjtectRevision+' '+line[1])+'\n'
    f=open(ExternalsFile,'w')
    f.write(Buffer)
    f.close()

    Cmd=f'svn propset svn:externals {TempWorkspace} -F {ExternalsFile}'
    CallSubprocess(Cmd)

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

    print (f'\n===== Update BIOS Version/Build ID =====')

    f=open(TempWorkspace+'\\HpPlatformPkg\\BLD\\BiosId.env','r')
    contents=f.readlines()
    f.close()

    BiosIdList=BiosId.split('.')
    OldBiosIdList=[00,00,00]
    OldBuildId=0000
    Buffer=''
    BiosIdEnvUpdate=False
    for line in contents:
        if 'VERSION_MAJOR' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{2}\b',line)
            if match:
                OldBiosIdList[1]='%02d' % int(match.group(0),16)
                # print (OldBiosIdList[1])
            line ='VERSION_MAJOR     = '+ ('%02X' % int(BiosIdList[1]))+'\n'
        if 'VERSION_MINOR' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{2}\b',line)
            if match:
                OldBiosIdList[2]='%02d' % int(match.group(0),16)
                # print (OldBiosIdList[2])
            line ='VERSION_MINOR     = '+ ('%02X' % int(BiosIdList[2]))+'\n'
        if 'VERSION_FEATURE' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{2}\b',line)
            if match:
                OldBiosIdList[0]='%02d' % int(match.group(0),16)
                # print (OldBiosIdList[0])
            line ='VERSION_FEATURE   = '+ ('%02X' % int(BiosIdList[0]))+'\n'
        if 'BUILD_ID' in line:
            # print (line.strip())
            match=re.search(r'\b[0-9A-Fa-f]{4}\b',line)
            if match:
                OldBuildId='%04d' % int(match.group(0))
            line ='BUILD_ID          = '+ ('%04d' % int(BuildId))+'\n'
        Buffer=Buffer+line

    for idx in range(0, len(OldBiosIdList), 1):
        # print (f'Old: {OldBiosIdList[idx]}, New: {int(BiosIdList[idx])}')
        if int(OldBiosIdList[idx]) != int(BiosIdList[idx]):
            # print (f'BiosIdEnvUpdate: {BiosIdEnvUpdate}')
            BiosIdEnvUpdate=True

    if int(OldBuildId) != int(BuildId):
        # print (f'BiosIdEnvUpdate: {BiosIdEnvUpdate}')
        BiosIdEnvUpdate=True

    if BiosIdEnvUpdate == False:
        print (f'BiosId.env no need to update!')
    else:
        print (Buffer)
        f=open(TempWorkspace+'\\HpPlatformPkg\\BLD\\BiosId.env','w')
        f.write(Buffer)
        f.close()

        MessageBuffer=MessageBuffer+f'\nUpdate BiosId.env\n'
        MessageBuffer=MessageBuffer+f'   Version : {BiosId}\n'
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
    CreateStageBranch()
    CheckoutNewStageCFUrl()
    UpdateExternal()
    UpdateBiosId()
    CommitPegAndBiosId()
    if (os.path.exists(MessageFile)):
        os.remove(MessageFile)
    if (os.path.exists(ExternalsFile)):
        os.remove(ExternalsFile)
    if (os.path.exists(TempWorkspace)):
        shutil.rmtree(TempWorkspace)

    print (f'\n===== StagingCF Create Done =====')
    print (f'\nStaging URL:')        
    print (f'  {NewStageCFUrl}')
