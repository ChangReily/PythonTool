import os
import subprocess

##
## Parse setting of Parameter.txt 
##
ParameterFilePtr =open('Parameter.txt','r')
while True :
    ParameterLine = ParameterFilePtr.readline()
    if ("" != ParameterLine):
        ParameterLine=ParameterLine.strip()
        if  ParameterLine=="":
            continue
        if '#' in ParameterLine:
            continue
        ParamterName,ParamterValue= ParameterLine.split("=")
        ParamterName=ParamterName.strip()
        ParamterValue=ParamterValue.strip()
        #print ParamterName+"="+ParamterValue
        if 'SvnServerUrl' ==  ParamterName:
            SvnServerUrl=ParamterValue
        elif 'ProjectPath' ==  ParamterName:
            ProjectPath=ParamterValue
        elif 'WorkingCopyPath' ==  ParamterName:
            WorkingCopyPath=ParamterValue
        elif 'Version' ==  ParamterName:
            Version=ParamterValue
        else:
            print 'Empty'
    else :
        #print "file finished"
        break
ParameterFilePtr.close()

##
## Console out the Setting
##
WorkingCopyPath = WorkingCopyPath + Version
print 'SvnServerUrl   : ' + SvnServerUrl
print 'ProjectPath    : ' + ProjectPath
print 'WorkingCopyPath: ' + WorkingCopyPath
print 'Version        : ' + Version

##
## Get the External Link properity
##
cmd='svn propget svn:externals -r '+ Version +' ' + SvnServerUrl + ProjectPath + ' > OldExternal.txt'
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
cmd = 'svn checkout -r ' + Version + ' ' + SvnServerUrl+ ProjectPath+' '+ os.path.realpath(WorkingCopyPath) + '  --ignore-externals'
#print cmd
Process = subprocess.call(cmd, shell=True )

##
## Set New External Link Setting
##
cmd = 'svn propset svn:externals '+ os.path.realpath(WorkingCopyPath) + ' -F NewExternal.txt'
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

cmd = 'svn switch --relocate '+SvnServerUrl+ProjectPath+' '+'https://csvnaus-pro.austin.hpicorp.net:20181/'+ProjectPath
print cmd


print 
