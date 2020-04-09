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

##########################################################################
# BIOS Folder Class
##########################################################################
class BiosFolderClass(object):
    def __init__(self, ProjectFolder):
        self.AllList=None
        self.BiosShareFolderPath='D:\\JenkinsBuild'
        self.ProjectName=ProjectFolder
        self.GetAllList(self.ProjectName)
        
    def GetAllList(self, ProjectFolder):
        CmdStr=f'dir {self.BiosShareFolderPath}\\{ProjectFolder} /OD > List.txt'
        CallSubprocess(CmdStr).StdoutBuffer()
        
        self.AllList=[]
        f=open('List.txt','r')
        ListBuffer=f.readlines()
        for idx in range(0, len(ListBuffer),1):
            line=ListBuffer[idx].rstrip()
            match = re.search(r'\d+/\d+/\d+\b', line)
            if match:
                rex = r'\s+'
                line=re.split(rex, line)
                # print (line)
                if not ((line[2] != '<DIR>') or (line[3] == '.') or (line[3] == '..')):
                    self.AllList.append(line)
                    # print (line)
        f.close()
        os.remove('List.txt')
                    
    def GetFolderContent(self,FolderName):
        CmdStr=f'dir {self.BiosShareFolderPath}\\{self.ProjectName}\\{FolderName}'
        stdoutBuffer=CallSubprocess(CmdStr).StdoutBuffer()
        Content=[]
        for line in stdoutBuffer:
            match = re.search(r'\d+/\d+/\d+\b', line)
            if match:
                rex = r'\s+'
                line=re.split(rex, line)
                if not ((line[3] == '.') or (line[3]== '..')):
                    FileName=line[3]
                    Content.append(FileName)
        return Content

    def GetFolderNameByDate(self,delta_days):
        # Data format mm/dd/YYYY
        LastFolderDate=self.AllList[-1][0].split('/')
        print (f'Last  Date: {LastFolderDate[2]}/{LastFolderDate[0]}/{LastFolderDate[1]} #{self.AllList[-1][3]}', file=sys.stdout, flush=True)
        DeltaDateTime=datetime.date(int(LastFolderDate[2]),int(LastFolderDate[0]),int(LastFolderDate[1])) + datetime.timedelta(days=delta_days)

        for index in range((len(self.AllList)-1),-1,-1):
            FolderDate=self.AllList[index][0].split('/')
            SearchDate=datetime.date(int(FolderDate[2]),int(FolderDate[0]),int(FolderDate[1]))
            if(DeltaDateTime >= SearchDate):
                break
        print (f'Delta Date: {FolderDate[2]}/{FolderDate[0]}/{FolderDate[1]} #{self.AllList[index][3]} (Delta: {delta_days} days)', file=sys.stdout, flush=True)
        return self.AllList[index][3]

    def GetPreviousBuildNumByFolderDate(self):
        PreviousBuildNum=self.GetFolderNameByDate(-1)
        BiosFileName=self.GetFolderContent(PreviousBuildNum)       
        return PreviousBuildNum,BiosFileName[0]

    def LastBuildNum(self, BuildTarget):
        LastLineNum=len(self.AllList)-1
        LastBuildNumber=self.AllList[LastLineNum][3]
        FileList=self.GetFolderContent(LastBuildNumber)
        # print (f'Last Build Number: {LastBuildNumber}')
        # print (f'FileList: {FileList}')
        for idx in range(0, len(FileList), 1):
            if BuildTarget in FileList[idx]:
                FileName=FileList[idx]
        
        print (f'Build Num: {LastBuildNumber}, BiosPackage: {FileName}', file=sys.stdout, flush=True)
        # return LastBuildNumber,FileName
        return os.path.join(os.path.join(self.BiosShareFolderPath, self.ProjectName), os.path.join(LastBuildNumber, FileName))


def UnzipFile(FilePath, ExtractPath):
    CmdStr=f'"{ZipToolPath}" x {FilePath} -o{ExtractPath} -y -r'
    Buffer=CallSubprocess(CmdStr).StdoutBuffer()
    print ('--------------------')
    for idx in range(1, len(Buffer), 1):
        print (Buffer[idx])
    print ('--------------------\n')
    return

def GetBiosBinPath(TempFolder):
    Found=False
    TargetBiosPath=''
    CmdStr=f'dir {TempFolder} /b'
    Buffer=CallSubprocess(CmdStr).StdoutBuffer()
    for idx in range(0, len(Buffer), 1):
        match = re.search('T95_[0-9A-Fa-f]{6}_[0-9A-Fa-f]{2}.bin', Buffer[idx])
        if match:
            # print (Buffer[idx])
            BiosName=Buffer[idx].strip()
            Found=True
        # print (Buffer[idx])
    if Found==True:
        TargetBiosPath=os.path.join(TempFolder, BiosName)
    print (TargetBiosPath)
    return TargetBiosPath
def ZipBiosBin(BiosBinPath):
    ZipFileName=os.path.splitext(os.path.basename(BiosBinPath))[0]
    ZipFileDir=os.path.dirname(BiosBinPath)
    ZipBiosBinCmd=f'"{ZipToolPath}" a {ZipFileDir}\\{ZipFileName}.7z {BiosBinPath}'
    Buffer=CallSubprocess(ZipBiosBinCmd).StdoutBuffer()
    print ('--------------------')
    for idx in range(1, len(Buffer), 1):
        print (Buffer[idx])
    print ('--------------------\n')
    return f'{ZipFileDir}\\{ZipFileName}.7z'

if __name__ == "__main__":
    BiosStorePath=os.getenv('BiosStorePath')
    Workspace=os.getenv('WORKSPACE')
    BuildNumber=os.getenv('BUILD_NUMBER')

    TargetFolder=os.path.join(Workspace, f'Build_{BuildNumber}')
    if os.path.isdir(TargetFolder) == False:
        os.mkdir(TargetFolder)
        os.mkdir(os.path.join(TargetFolder, 'Release'))
        os.mkdir(os.path.join(TargetFolder, 'Debug'))

    ReleaseBioaPackage=os.path.join(BiosStorePath,'Fv_Release.7z')
    UnzipFile(ReleaseBioaPackage, Workspace)
    TempFolder=os.path.join(Workspace, os.path.splitext(os.path.basename(ReleaseBioaPackage))[0])
    BiosBinPath=GetBiosBinPath(TempFolder)
    # ZipReleaseBiosFile=ZipBiosBin(BiosBinPath)
    shutil.copy2(BiosBinPath, os.path.join(TargetFolder, 'Release'))

    DebugBioaPackage=os.path.join(BiosStorePath,'Fv_Debug.7z')
    UnzipFile(DebugBioaPackage, Workspace)
    TempFolder=os.path.join(Workspace, os.path.splitext(os.path.basename(DebugBioaPackage))[0])
    BiosBinPath=GetBiosBinPath(TempFolder)
    shutil.copy2(BiosBinPath, os.path.join(TargetFolder, 'Debug'))
    # ZipBiosBin(BiosBinPath)

    ZipBiosBinCmd=f'"{ZipToolPath}" a -t7z {TargetFolder}.7z {TargetFolder}'
    Buffer=CallSubprocess(ZipBiosBinCmd).StdoutBuffer()
    print ('--------------------')
    for idx in range(1, len(Buffer), 1):
        print (Buffer[idx])
    print ('--------------------\n')
    

    
