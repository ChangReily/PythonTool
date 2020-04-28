import time
import os
import pysvn
import sys

def ssl_server_trust_prompt( trust_dict ):
    return (True    # server is trusted
           ,trust_dict["failures"]
           ,True)   # save the answer so that the callback is not called again

client = pysvn.Client()
client.exception_style = 1
client.callback_ssl_server_trust_prompt = ssl_server_trust_prompt
work_path = 'https://svn-pro.corp.hpicloud.net:20181/svn/svn-psgfw-platform14/'

FILE_CHANGE_INFO = {
        pysvn.diff_summarize_kind.normal: ' ',
        pysvn.diff_summarize_kind.modified: 'M',
        pysvn.diff_summarize_kind.delete: 'D',
        pysvn.diff_summarize_kind.added: 'A',
        }


argc = len(sys.argv )
if argc == 2:
  SvnRev = sys.argv[1]
  # DstDir = sys.argv[2]    
else:
  print  
  print  
  print "The command should follow below format:" 
  # print "  Usage: " + os.path.basename (sys.argv[0]) + " <SvnRevision> <Destination>"
  print "  Usage: " + os.path.basename (sys.argv[0]) + " <SvnRevision>"
  exit ()
  

CheckLogRevision=int(SvnRev)
TargetFolder="C:\\Users\\changre\\Desktop\\python_svn_tool\\CatSolution\\"+str(CheckLogRevision)
TargetFolder=os.getcwd()+"\\"+str(CheckLogRevision)
TargetFolder = os.path.realpath (TargetFolder)

# CheckLogRevision=83208
# TargetFolder = os.path.realpath (DstDir)

#
# Define Head version and End Verison
#
head = pysvn.Revision(pysvn.opt_revision_kind.number, CheckLogRevision)
end = pysvn.Revision(pysvn.opt_revision_kind.number, CheckLogRevision)

#
# Check the target folder exist or not and create the folder
#
if not os.path.exists (TargetFolder):
    os.makedirs (TargetFolder)

#
# Get the reversion log
#
log_messages = client.log(work_path, revision_start=head, revision_end=end, discover_changed_paths=True, limit=1,)
log_messages.reverse()
for log in log_messages:
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date))
    print
    print '[%s]' % (log.revision.number)
    print '%s\t%s' % (timestamp, log.author)
    print '%s\n' % (log.message)
    # paths = [p.path for p in log.data['changed_paths']]
    # for path in paths:
        # print("Path: " + str(path)) 
       
        
print '--------File changed--------'
head = pysvn.Revision(pysvn.opt_revision_kind.number, CheckLogRevision-1)
end = pysvn.Revision(pysvn.opt_revision_kind.number, CheckLogRevision)




FilePtr = open (TargetFolder+ '/' + str(CheckLogRevision)+'.txt', "w")
FilePtr.write ('['+str(log.revision.number)+']'+'\r\n' + str(timestamp) +'\t'+ log.author+'\r\n'+ log.message)
FilePtr.close()

FilePtr = open (TargetFolder+ '/' + str(CheckLogRevision)+'.txt', "a")
FilePtr.write('\r\n\r\n--------File changed--------\r\n')
summary = client.diff_summarize(work_path, head, work_path, end)
for info in summary:
    path = info.path
    if info.node_kind == pysvn.node_kind.dir:
        path += '/'
    file_changed = FILE_CHANGE_INFO[info.summarize_kind]
    prop_changed = ' '
    if info.prop_changed:
        prop_changed = 'M'
    print file_changed + ' ' + path
    FilePtr.write(file_changed + ' ' + path+'\r\n')
print
FilePtr.close()



print
print 'Processing Solution Export.................'

for info in summary:
    path = info.path
    file_changed = FILE_CHANGE_INFO[info.summarize_kind]
    SvnPath=path
  
    EndFilePath=os.path.realpath (TargetFolder+ '/'+str(CheckLogRevision)+'/' + path)
    HeadFilePath=os.path.realpath (TargetFolder+ '/'+str(CheckLogRevision-1)+'/' + path)
    
    EndDirPath=os.path.dirname(EndFilePath)  
    if not os.path.exists(EndDirPath):
        os.makedirs(EndDirPath)
        
    HeadDirPath=os.path.dirname(HeadFilePath)
    if not os.path.exists(HeadDirPath):
        os.makedirs(HeadDirPath)

    if info.node_kind == pysvn.node_kind.dir:
        path += '/'

    if info.summarize_kind == pysvn.diff_summarize_kind.modified:
        print file_changed + ' ' + path
        
        FilePtr = open (EndFilePath, "wb")
        FilePtr.write (client.cat (work_path+SvnPath, end, end))
        FilePtr.close()

        FilePtr = open (HeadFilePath, "wb")
        FilePtr.write (client.cat (work_path+SvnPath, head, head))
        FilePtr.close()

        
    if info.summarize_kind == pysvn.diff_summarize_kind.added:
        if not os.path.isdir(EndFilePath):
            print file_changed + ' ' + path
            FilePtr = open (EndFilePath, "wb")
            FilePtr.write (client.cat (work_path+SvnPath, end, end))
            FilePtr.close()
        
    if info.summarize_kind == pysvn.diff_summarize_kind.delete:
        if not os.path.isdir(HeadFilePath):
            print file_changed + ' ' + path
            FilePtr = open (HeadFilePath, "wb")
            FilePtr.write (client.cat (work_path+SvnPath, head, head))
            FilePtr.close()
            
        

print
print

