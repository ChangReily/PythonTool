import os
import subprocess

#
# Project Path
#
#ProjectPath=svn/svn-psgfw-platform14/trunk/Projects/BIOS17Rr/HpKirk
ProjectPath='/trunk/Projects/BIOS18GLK/HpBalos'

#
# Version number
#
Version=170705
Version=str(Version)
#
# The location of checkout or export path
#
WorkingCopyPath='D:\BIOS\BIOS18_HpBalos\Balos_'+Version


#
# Austin Server: https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14
# Local Server: svn://localhost/svn/svn-psgfw-platform14
#
AustinSvn='https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14'
LocaSvn='svn://15.38.78.211/svn/svn-psgfw-platform14'
SvnServerUrl=AustinSvn + ProjectPath
LocaSvnServerUrl=LocaSvn + ProjectPath

##
## Console out the Setting
##
print 'SvnServerUrl     : ' + SvnServerUrl
print 'LocalSvnServerUrl: ' + LocaSvnServerUrl 
print 'WorkingCopyPath  : ' + WorkingCopyPath
print 'Version          : ' + Version

##
## Get the External Link properity
##
cmd='svn propget svn:externals -r ' + Version + ' ' + SvnServerUrl + ' > OldExternal.txt'
print cmd
Process = subprocess.call(cmd,shell=True )

##
## Update External Link version for /svn/svn-psgfw-platform14/
##
OrgExternalLinkPtr = open ("OldExternal.txt","r")
NewExternalLinkPtr = open ("NewExternal.txt", "w")
while True :
    line = OrgExternalLinkPtr.readline()
    if '/svn/svn-psgfw-platform14/' in line:
        if '@' in line:
            NewExternalLinkPtr.write(line)
            continue
        a,b= line.split(" ")
        a=a+'@'+Version
        line = a+' '+b
    #print line        
    NewExternalLinkPtr.write(line)
    
    if ("" == line):
        #print "file finished"
        break

OrgExternalLinkPtr.close()
NewExternalLinkPtr.close()

##
## Checkout source code for specific version
##
cmd = 'svn checkout -r ' + Version + ' ' + LocaSvnServerUrl + ' ' + os.path.realpath(WorkingCopyPath) + '  --ignore-externals'
#print cmd
Process = subprocess.call(cmd, shell=True )

##
## Set New External Link Setting
##
cmd = 'svn propset svn:externals ' + os.path.realpath(WorkingCopyPath) + ' -F NewExternal.txt'
#print cmd
Process = subprocess.call(cmd, shell=True )

##
## Update it again
##
cmd = 'svn update -r ' + Version + ' ' + os.path.realpath(WorkingCopyPath)
#print cmd
Process = subprocess.call(cmd, shell=True )

##
## Remove temp file
##
os.remove("OldExternal.txt")
os.remove("NewExternal.txt")

cmd = 'svn relocate ' + LocaSvn +' ' + AustinSvn + ' ' + os.path.realpath(WorkingCopyPath)
print cmd
Process = subprocess.call(cmd, shell=True )


print 
