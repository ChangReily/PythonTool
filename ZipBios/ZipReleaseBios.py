import os
import sys
import subprocess
import datetime
import re
import shutil

ZipToolPath='C:\\Program Files\\7-Zip\\7z.exe'

################################################################################
#   Subprocess.popen call
################################################################################
class CallSubprocess(object):
    def __init__(self, CmdStr, PrintCmd=True, PrintStdout=False, PrintStderr=False, Timeout=None):
        self._ReturnCode=1
        self._Stdout=None
        self._Stderr=None
        self._CallSubprocess(CmdStr, PrintCmd, PrintStdout, PrintStderr, Timeout)

    def _CallSubprocess(self, CmdStr, PrintCmd, PrintStdout, PrintStderr, Timeout):
        if PrintCmd:
            print (CmdStr, file=sys.stdout, flush=True)
        Process=subprocess.Popen(CmdStr, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if Timeout != None:
            Timeout=int(Timeout)

        try:
            ReturnCode = Process.wait(Timeout)
        except subprocess.TimeoutExpired:
            Process.kill()

        ReturnCode=Process.returncode        
        StderrBuffer=None
        StdoutBuffer=None
        if (ReturnCode==0):
            StdoutBuffer=[]
            for line in Process.stdout:
                line = line.rstrip()
                line = line.decode(encoding='UTF-8')
                StdoutBuffer.append(line)
                if PrintStdout:
                    print (line, file=sys.stdout, flush=True)
        else:        
            StderrBuffer=[]
            for line in Process.stderr:
                line = line.rstrip()
                line = line.decode(encoding='UTF-8')    
                StderrBuffer.append(line)
                if PrintStderr:
                    print (line, file=sys.stdout, flush=True)
        
        self._ReturnCode=ReturnCode
        self._Stderr=StderrBuffer
        self._Stdout=StdoutBuffer
        # print (f'_CallSubprocess Return: {ReturnCode}', file=sys.stdout, flush=True)
        # print (f'_CallSubprocess _Stdout: {self._Stdout}', file=sys.stdout, flush=True)
        return 

    def ReturnCode(self):
        return self._ReturnCode
    
    def StdoutBuffer(self):
        return self._Stdout


def UnzipFile(FilePath, ExtractPath):
    CmdStr=f'"{ZipToolPath}" x {FilePath} -o{ExtractPath} -y -r'
    Buffer=CallSubprocess(CmdStr).StdoutBuffer()
    print ('--------------------')
    for idx in range(1, len(Buffer), 1):
        print (Buffer[idx])
    print ('--------------------\n')
    return

def GetBiosBinPath(TempFolder, BiosId):
    Found=False
    TargetBiosPath=''
    CmdStr=f'dir {TempFolder} /b'
    Buffer=CallSubprocess(CmdStr).StdoutBuffer()
    for idx in range(0, len(Buffer), 1):
        match = re.search(str(BiosId)+'_[0-9A-Fa-f]{6}_[0-9A-Fa-f]{2}.bin', Buffer[idx])
        if match:
            # print (Buffer[idx])
            BiosName=Buffer[idx].strip()
            Found=True
        # print (Buffer[idx])
    if Found==True:
        TargetBiosPath=os.path.join(TempFolder, BiosName)
    print (TargetBiosPath)
    return TargetBiosPath, BiosName

if __name__ == "__main__":
    BiosStorePath=os.getenv('BiosStorePath')
    Workspace=os.getenv('WORKSPACE')
    BuildNumber=os.getenv('BUILD_NUMBER')
    BiosId=os.getenv('BIOS_ID')

    TargetFolder=os.path.join(Workspace, f'Build_{BuildNumber}')
    if os.path.isdir(TargetFolder) == False:
        os.mkdir(TargetFolder)
        os.mkdir(os.path.join(TargetFolder, 'Release'))

    ReleaseBioaPackage=os.path.join(BiosStorePath,'Fv_Release.7z')
    UnzipFile(ReleaseBioaPackage, Workspace)
    TempFolder=os.path.join(Workspace, os.path.splitext(os.path.basename(ReleaseBioaPackage))[0])
    BiosBinPath, BiosName=GetBiosBinPath(TempFolder, BiosId)
    shutil.copy2(BiosBinPath, os.path.join(TargetFolder, 'Release'))

    shutil.copy2(BiosBinPath, BiosStorePath)
    NewBiosName=f'{os.path.splitext(BiosName)[0]}_R{os.path.splitext(BiosName)[1]}'
    os.rename(os.path.join(BiosStorePath, BiosName), os.path.join(BiosStorePath, NewBiosName))

    ZipBiosBinCmd=f'"{ZipToolPath}" a -t7z {TargetFolder}.7z {TargetFolder}'
    Buffer=CallSubprocess(ZipBiosBinCmd).StdoutBuffer()
    print ('--------------------')
    for idx in range(1, len(Buffer), 1):
        print (Buffer[idx])
    print ('--------------------\n')
    

    
