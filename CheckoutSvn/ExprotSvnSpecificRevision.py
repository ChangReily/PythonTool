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
## Export root folder
##
cmd = 'svn export -r ' + Version + ' ' + SvnServerUrl+ ProjectPath+' '+ os.path.realpath(WorkingCopyPath) + '  --ignore-externals'
print cmd
Process = subprocess.call(cmd, shell=True )

##
## Get the External Link properity
##
cmd='svn propget svn:externals -r '+ Version +' ' + SvnServerUrl + ProjectPath
print cmd
Process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )
OutputBuffer,ErrorBuffer = Process.communicate()

##
## Export External link folders
##
ExternalsList= OutputBuffer.split("\r\n")
for i, LineStr in enumerate(ExternalsList):
    if ("" == LineStr):
        break
    
    SvnSubPath,Folder= LineStr.split(" ")
    if 'svn-psgfw-platform14' in SvnSubPath:
        if '@' in SvnSubPath:
            SvnSubPath_1,ExternalVersion=SvnSubPath.split('@')
            cmd = 'svn export -r '+ ExternalVersion +' '+ SvnServerUrl+ SvnSubPath_1+' '+ os.path.realpath(WorkingCopyPath+ '\\' +Folder)
        else:    
            cmd = 'svn export -r '+ Version +' '+ SvnServerUrl+ SvnSubPath+' '+ os.path.realpath(WorkingCopyPath+ '\\' +Folder)
    else:
        cmd = 'svn export '+ SvnServerUrl+ SvnSubPath+' '+ os.path.realpath(WorkingCopyPath+ '\\' +Folder)

    print cmd
    Process = subprocess.call(cmd, shell=True )

print 
