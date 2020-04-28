import os
import sys
import subprocess
import timeit

start = timeit.default_timer()

print " "   
WorkingCopyPath=os.getcwd()


argc = len(sys.argv)
if argc == 3:
  ProjectPath = sys.argv[1]
  DstDir = sys.argv[2]    
else:
  print "The command should follow below format:" 
  print "  " + os.path.basename (sys.argv[0]) + " SvnPath DstDir"
  print "  ex: CheckoutSvn.py /trunk/Projects/BIOS18GLK/HpBalos HpBalos_1"
  exit ()


#
# The location of checkout or export path
#
WorkingCopyPath=WorkingCopyPath+'\\'+DstDir

#
# Austin Server: https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14
# Local Server: svn://localhost/svn/svn-psgfw-platform14/trunk/project/bios18glk/hpbalos
#
AustinSvn='https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14'
LocaSvn='svn://localhost/svn/svn-psgfw-platform14'
SvnServerUrl=AustinSvn + ProjectPath
LocaSvnServerUrl=LocaSvn + ProjectPath

##
## Console out the Setting
##
#print 'SvnServerUrl     : ' + SvnServerUrl
print 'LocalSvnServerUrl: ' + LocaSvnServerUrl 
print 'WorkingCopyPath  : ' + WorkingCopyPath

#
#Checkout source code for specific version#
#
cmd = 'svn checkout' + ' ' + LocaSvnServerUrl + ' ' + os.path.realpath(WorkingCopyPath)
#print cmd
Process = subprocess.call(cmd, shell=True )

cmd = 'svn info' + ' ' + os.path.realpath(WorkingCopyPath)
Process = subprocess.call(cmd, shell=True )

cmd = 'svn relocate ' + LocaSvn +' ' + AustinSvn + ' ' + os.path.realpath(WorkingCopyPath)
print cmd
Process = subprocess.call(cmd, shell=True )

cmd = 'svn info' + ' ' + os.path.realpath(WorkingCopyPath)
Process = subprocess.call(cmd, shell=True )

stop = timeit.default_timer()

print('Time: ', stop - start) 
# print 
