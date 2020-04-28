import os
import subprocess
import re
import shutil

###############################################################################
# Project Configuration
###############################################################################
# HpBalos10
ProjectUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/branches/ProjectsCF/Bios17Platform/HpBalos'
StageCFUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/branches/StagingCF/Bios17Platform/HpBalos10'
BiosId='99.99.99'
BuildId='0000'

# # HpAloe10
# ProjectUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/branches/ProjectsCF/Bios17Platform/HpAloe10'
# StageCFUrl='https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/branches/StagingCF/Bios17Platform/HpAloe10'
# BiosId='99.99.99'
# BuildId='0000'


###############################################################################
# Global variable
###############################################################################
NewStageCFUrl=''
ProjtectRevision=''
CoreRevision=''
TempWorkspace=os.path.join(os.getcwd(), 'SvnTempFolder')
ExternalsFile=os.path.join(os.getcwd(), 'Externals.txt')
MessageFile=os.path.join(os.getcwd(), 'Message.txt')

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
    global NewStageCFUrl

    ProjectName=ProjectUrl.rsplit('/',1)[1]
    BiosIdList=BiosId.split('.')
    NewStageCFUrl=f'{StageCFUrl}/{BiosIdList[0]}{BiosIdList[1]}{BiosIdList[2]}_{BuildId}/{ProjectName}'
    SvnCopycmd=f'svn copy -m "Perpare {ProjectName} {BiosId} signing" --parents {ProjectUrl} {NewStageCFUrl}'
    print (f'\n===== Parsing INI file =====')
    print (f'{SvnCopycmd}')
    CallSubprocess(SvnCopycmd)
    return

###############################################################################
# Create branches/StagingCF/BiosXXplatform/'PlatformName'/'XXXXXX_XXXX'/'PlatformName'
# ex: branches/StagingCF/Bios17platform/HpBalos10/999999_0000/HpBalos
###############################################################################
def CreateStageBranch():
    global NewStageCFUrl

    ProjectName=ProjectUrl.rsplit('/',1)[1]
    BiosIdList=BiosId.split('.')
    NewStageCFUrl=f'{StageCFUrl}/{BiosIdList[0]}{BiosIdList[1]}{BiosIdList[2]}_{BuildId}/{ProjectName}'
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
    print (f'\n===== Update External PEG Number =====')

    #
    # Get svn/svn-psgfw-platform14 Repository Root
    #
    process=subprocess.Popen(['svn', 'info', ProjectUrl], shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    return

###############################################################################
# Update BIOS version/Build ID
###############################################################################
def UpdateBiosId():
    print (f'\n===== Update BIOS Version/Build ID =====')
    global TempWorkspace
    f=open(TempWorkspace+'\\HpPlatformPkg\\BLD\\BiosId.env','r')
    contents=f.readlines()
    f.close()
    BiosIdList=BiosId.split('.')
    Buffer=''
    for line in contents:
        if 'VERSION_MAJOR' in line:
            line ='VERSION_MAJOR     = '+ ('%02X' % int(BiosIdList[1]))+'\n'
        if 'VERSION_MINOR' in line:
            line ='VERSION_MINOR     = '+ ('%02X' % int(BiosIdList[2]))+'\n'
        if 'VERSION_FEATURE' in line:
            line ='VERSION_FEATURE   = '+ ('%02X' % int(BiosIdList[0]))+'\n'
        if 'BUILD_ID' in line:
            line ='BUILD_ID          = '+ ('%04d' % int(BuildId))+'\n'
        Buffer=Buffer+line
    print (Buffer)

    f=open(TempWorkspace+'\\HpPlatformPkg\\BLD\\BiosId.env','w')
    f.write(Buffer)
    f.close()

    return

###############################################################################
# Commit PEG number and BIOS version/Build ID
###############################################################################
def CommitPegAndBiosId():
    global ProjtectRevision
    global CoreRevision
    global TempWorkspace
    print (f'\n===== Commit External and BiosId.env change =====')
    Buffer=''
    Buffer=Buffer+f'1. Update PEG number\n'
    Buffer=Buffer+f'     Platform: {ProjtectRevision}\n'
    Buffer=Buffer+f'     Core    : {CoreRevision}\n'
    Buffer=Buffer+f'2 Update BiosId.env\n'
    Buffer=Buffer+f'     Version : {BiosId}\n'
    Buffer=Buffer+f'     Build ID: {BuildId}'
    print ('** Commit Message Start **')
    print (Buffer)
    print ('** Commit Message End **')
    File=open(MessageFile, 'w')
    File.write(Buffer)
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
    global NewStageCFUrl
    # ParsingIniFile()
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
    print (f'{NewStageCFUrl}')
