import os
import sys
import re
import subprocess

# SoureFolder=r'D:\BIOS\BIOS18GLK\svn-psgfw-platform14\branches\ProjectsCF\Bios17Platform\HpBalos'
# TargetSprint=''
TargetSprint='Sprint20-07'


def CheckExternalLink(SvnServerUrl, ExternalLink):
    # print (ExternalLink)
    FolderPath=ExternalLink.split(' ')[1]
    ExternalUrl=ExternalLink.split(' ')[0]
    ReturnLink=ExternalUrl

    if SvnServerUrl != '':
        ExternalUrl=ExternalUrl.rsplit('/',1)[0]
        Cmd='svn list {0}{1}'.format(SvnServerUrl,ExternalUrl)
        print ('Checking...{0}'.format(ExternalUrl))
        process=subprocess.Popen(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutput = process.communicate()[0]
                
        SprintList=list(stdoutput.decode('UTF-8','ignore').split())
        # print (SprintList)
        if TargetSprint != '':
            # Update specific Sprint version
            # Method 1: Search less than Target Sprint
            # Method 2: Focus on Sprint
            SearchMethod=1
            if SearchMethod == 1:
                # Method 1: Search less than Target Sprint
                TempTargetSprint = re.sub('Sprint', '', TargetSprint)
                TempTargetSprint = re.sub('-', '', TempTargetSprint)
                TempTargetSprint = float(TempTargetSprint)
                # print (f'Target: {TempTargetSprint}')
                for idx in range(len(SprintList)-1, 0, -1):
                    SearchSprint=SprintList[idx].rsplit('/',1)[0]
                    SearchSprint = re.sub('Sprint', '', SearchSprint)
                    SearchSprint = re.sub('-', '', SearchSprint)
                    SearchSprint = float(SearchSprint)
                    # print (f'Search: {SearchSprint}')
                    if TempTargetSprint >= SearchSprint:
                        LastVersion=SprintList[idx].rsplit('/',1)[0]
                        ReturnLink='{0}/{1}'.format(ExternalUrl,LastVersion)
                        break
            if SearchMethod == 2:
                for line in SprintList:
                    line = line.rstrip()
                    match = re.search(TargetSprint, line)
                    if match:
                        ReturnLink='{0}/{1}'.format(ExternalUrl,LastVersion)
        else:
            # Update Latest Sprint version
            LastVersion=SprintList[-1].rsplit('/',1)[0]
            ReturnLink=ExternalUrl+'/'+LastVersion

    return ('{0} {1}'.format(ReturnLink,FolderPath))

if __name__ == "__main__":
    SoureFolder=input('Source Path: ')
    if SoureFolder != '':
        
        Demarcation='================================================================================'
        print (Demarcation)
        # Get svn/svn-psgfw-platform14 Repository Root
        Cmd='svn info {0}'.format(SoureFolder)
        # print (Cmd)
        process=subprocess.Popen(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        PlatformSvnRootUrl=''
        for line in process.stdout:
            line = line.rstrip().decode('UTF-8','ignore')
            if line != '':
                print (line)
                match = re.search(r'Repository Root: (.*)', line)
                if match:
                    PlatformSvnRootUrl = match.group(1)
        # print (f'Repository Root: {PlatformSvnRootUrl}')
        if PlatformSvnRootUrl == '':
            raise ValueError('Unable get Repository Root!')


        # Get SVN server location
        print (Demarcation)
        SvnServerUrl=''
        SvnServerUrl=PlatformSvnRootUrl.rsplit('/',2)[0]
        print ('Extract SVN Host URL to check Core path:')
        print ('  {0}'.format(SvnServerUrl))
        
        # Update external links form Project to get HpCore path
        print ('')
        print (Demarcation)
        if TargetSprint != '':
            print ('Update Specific Sprint version! - {0}\n'.format(TargetSprint))
        else:
            print ('Update Latest Sprint version!\n')

        Buffer=''
        process=subprocess.Popen(['svn', 'propget', 'svn:externals',SoureFolder], shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in process.stdout:
            line = line.rstrip().decode('UTF-8','ignore')
            regex = re.search('/svn/svn-psgfw-core/ReleaseTags', line)
            if regex != None:
                OriginalLink=line
                CheckLink=CheckExternalLink(SvnServerUrl, line)
                if OriginalLink != CheckLink:
                    line=CheckLink
                    print ('   Original: {0}'.format(OriginalLink))
                    print ('   Updated : {0}'.format(CheckLink))
            Buffer=Buffer+line+'\n'
        print ('Done..........')

        # Write the externals to TXT file
        TempTxtFile='externals.txt'
        f=open(TempTxtFile,'w')
        f.write(Buffer)
        f.close()

        # Use svn command to set external links
        print ('')
        print (Demarcation)
        print ('Set new external link to {0}'.format(SoureFolder))
        Cmd='svn propset svn:externals {0} -F {1}'.format(SoureFolder,TempTxtFile)
        print (Cmd)
        stdoutput=subprocess.Popen(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        print (stdoutput.decode('UTF-8','ignore'))

        # Delete the TXT file
        os.remove(TempTxtFile)
        os.system('pause')

    
