import time
import os
import sys
from datetime import date, timedelta
from array import array

import pysvn

def ssl_server_trust_prompt( trust_dict ):
    return (True    # server is trusted
           ,trust_dict["failures"]
           ,True)   # save the answer so that the callback is not called again
 
client = pysvn.Client()
client.exception_style = 1
client.callback_ssl_server_trust_prompt = ssl_server_trust_prompt


SvnUrlPath = 'https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14/'
PlatformPkgPath= 'trunk/Projects/BIOS17Rr/HpKirk'
ChipsetPkgPath='trunk/Chipset/AMD/RavenRidge'
PlatformCommonPkgPath='trunk/Chipset/AMD/AmdPlatformCommonPkgV9'
IA32FamilyCpuPkgPath='/trunk/Chipset/AMD/AMDIA32FamilyCpuPkgV9'

SvnRevList =[]


argc = len(sys.argv )
if argc == 4:
  if str(sys.argv[1]) == str('-r'):
    StartRev = sys.argv[2]
    EndRev = sys.argv[3]
    CheckStart = pysvn.Revision(pysvn.opt_revision_kind.number, int(StartRev)-1)
    CheckEnd = pysvn.Revision(pysvn.opt_revision_kind.number, int(EndRev)+1) 
  else:
    print "  Usage: " + os.path.basename (sys.argv[0]) + " -r <StartSvnRevision> <EndSvnRevision>"
    exit()
elif argc == 8:
  if str(sys.argv[1]) == str('-d'):
    StartDateYear = sys.argv[2]
    StartDateMonth = sys.argv[3]
    StartDateDay = sys.argv[4]
    EndDateYear = sys.argv[5]
    EndDateMonth = sys.argv[6]
    EndDateDay = sys.argv[7]
  
    startDate = date(int(StartDateYear), int(StartDateMonth), int(StartDateDay))
    endDate = date(int(EndDateYear), int(EndDateMonth), int(EndDateDay))+timedelta(days=1)

    StartTimeStruct = time.strptime(str(startDate),"%Y-%m-%d")
    EndTimeStruct = time.strptime(str(endDate),"%Y-%m-%d")

    CheckStart = pysvn.Revision(pysvn.opt_revision_kind.date, time.mktime(StartTimeStruct))
    CheckEnd = pysvn.Revision(pysvn.opt_revision_kind.date, time.mktime(EndTimeStruct))
  else:
    print "  Usage: " + os.path.basename (sys.argv[0]) + " -d <StartDateYear> <StartDateMonth> <StartDateDay> <EndDateYear> <EndDateMonth> <EndDateDay>"
else:
  print  
  print "The command should follow below format:" 
  # print "  Usage: " + os.path.basename (sys.argv[0]) + " <SvnRevision> <Destination>"
  print "  Usage: " + os.path.basename (sys.argv[0]) + " -r <StartSvnRevision> <EndSvnRevision>"
  print "  Usage: " + os.path.basename (sys.argv[0]) + " -d <StartDateYear> <StartDateMonth> <StartDateDay> <EndDateYear> <EndDateMonth> <EndDateDay>"
  exit ()




PlatformPkgSvnLog = client.log(SvnUrlPath+PlatformPkgPath, revision_start=CheckStart, revision_end=CheckEnd)
for log in PlatformPkgSvnLog:
    SvnRevList.append(log.revision.number)
##    print '[%s] PlatformPkgSvnLog' % (log.revision.number)
##    print '\t%s\t%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date)), log.author)

ChipsetPkgSvnLog = client.log(SvnUrlPath+ChipsetPkgPath, revision_start=CheckStart, revision_end=CheckEnd)
for log in ChipsetPkgSvnLog:
    SvnRevList.append(log.revision.number)
##    print '[%s] ChipsetPkgSvnLog' % (log.revision.number)
##    print '\t%s\t%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date)), log.author)

PlatformCommonPkgSvnLog = client.log(SvnUrlPath+PlatformCommonPkgPath, revision_start=CheckStart, revision_end=CheckEnd)
for log in PlatformCommonPkgSvnLog:
    SvnRevList.append(log.revision.number)
##    print '[%s] PlatformCommonPkgSvnLog' % (log.revision.number)
##    print '\t%s\t%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date)), log.author)

IA32FamilyCpuPkgSvnLog = client.log(SvnUrlPath+IA32FamilyCpuPkgPath, revision_start=CheckStart, revision_end=CheckEnd)
for log in PlatformCommonPkgSvnLog:
    SvnRevList.append(log.revision.number)
##    print '[%s] IA32FamilyCpuPkgSvnLog' % (log.revision.number)
##    print '\t%s\t%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date)), log.author)



SvnRevList=list(set(SvnRevList))
SvnRevList.sort(reverse=True)

for SvnNum in SvnRevList:
    for log in PlatformPkgSvnLog:
        if SvnNum == log.revision.number:
            print '[%s]\tHpPlatformPkg\t\t\t%s %s' % (log.revision.number, time.strftime('%Y-%m-%d %H:%M', time.localtime(log.date)), log.author)
            
    for log in ChipsetPkgSvnLog:
        if SvnNum == log.revision.number:
            print '[%s]\tAgesa/ChipsetPkg\t\t%s %s' % (log.revision.number, time.strftime('%Y-%m-%d %H:%M', time.localtime(log.date)), log.author)

    for log in PlatformCommonPkgSvnLog:
        if SvnNum == log.revision.number:
            print '[%s]\tAmdPlatformCommonPkg\t%s %s' % (log.revision.number, time.strftime('%Y-%m-%d %H:%M', time.localtime(log.date)), log.author)

    for log in IA32FamilyCpuPkgSvnLog:
        if SvnNum == log.revision.number:
            print '[%s]\tAMDIA32FamilyCpuPkg\t%s %s' % (log.revision.number, time.strftime('%Y-%m-%d %H:%M', time.localtime(log.date)), log.author)

print ''
SvnLog = client.log(SvnUrlPath, revision_start=CheckStart, revision_end=CheckEnd, discover_changed_paths=True)
for SvnNum in SvnRevList:
    for log in SvnLog:
        if SvnNum == log.revision.number:
            print '=====[%s]==================================================================' % (log.revision.number)
            print '%s\t%s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date)), log.author)
            print '%s\n' % (log.message)

            paths = [p.path for p in log.data['changed_paths']]
            paths.sort(reverse=False)
            print '-----File Change-----'
            for path in paths:
                print(str(path))
            print ''
