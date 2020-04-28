#  ##########################################################################  #
#  To import generic libraries
#  ##########################################################################  #
import smtplib, os, sys, re, subprocess, pprint, operator
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


global SMTPServer, SMTPPort
SMTPServer = "smtp1.hp.com"
SMTPPort = "25"


class SvnNotificationStruct:
    Revision = 0
    Author = ''
    Date = '2018-01-01'
    ChgPath = 'File Changed:\n'
    ChgTitle = '\[BIOS18\]'
    ChgLog = ''
    EmailSender = ''
    EmailRecipientList = ''

    def __init__(self, rev):
      self.Revision = rev

    def SetAuthor(self, svnauthor):
      self.Author = svnauthor
      self.EmailSender = svnauthor +'@hp.com'
      self.EmailRecipientList = self.EmailSender


global SvnInfos
SvnInfos = SvnNotificationStruct(0)

global msg
# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')


def SvnInfoGrabber(rev):
    global text

    process = subprocess.Popen(['svn', 'log', '-r', rev, '-v'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_out, process_err = process.communicate()
    revfdBuffer = process_out.decode("utf-8", 'ignore').splitlines()
    revfdBufferCounts=len(revfdBuffer)
    #print(revfdBuffer)
   
    # revfdBuffer[0]   = '------------------------------------------------------------------------'
    # revfdBuffer[1]   = 'revision | Author | Date | lines'
    # revfdBuffer[2]   = 'Changed paths:'
    # revfdBuffer[3~n] = ' M Path'
    # revfdBuffer[n]   = ' Change Notes'
    # revfdBuffer[n+1] = '------------------------------------------------------------------------'

    # capture revision#
    regex = re.search('[r][0-9]{0,}', revfdBuffer[1])
    SvnInfos.Revision = regex.group().lstrip('r')

    # capture Author
    regex = re.search('\|\s.[^|]{0,}\s\|', revfdBuffer[1])
    SvnInfos.SetAuthor(regex.group().lstrip('|').rstrip('|').lstrip(' '))
    # Update Author Name
    TestAuthor='reily.chang'
    TestAuthor1 = revfdBuffer[1].split(" | ")[1]
    if (TestAuthor == TestAuthor1):
        SvnInfos.Author = 'Change, Reily'

    # capture Date
    regex = re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}', revfdBuffer[1])
    SvnInfos.Date = regex.group().lstrip('|').rstrip('|').lstrip(' ')
    SvnInfos.Date=SvnInfos.Date.replace('-','/')
    
    # Build modified file path information
    for idx in range(0,revfdBufferCounts,1):
        if revfdBuffer[idx] == "Changed paths:":
            MpathStartLine = idx + 1
        if revfdBuffer[idx] == "":
            MPathEndLine = idx
            break

    for idx in range(MpathStartLine, MPathEndLine, 1):
         SvnInfos.ChgPath = SvnInfos.ChgPath + revfdBuffer[idx] + '\n'

    SvnInfos.ChgPath = SvnInfos.ChgPath.replace("  M ", "Modified : ")  
    SvnInfos.ChgPath = SvnInfos.ChgPath.replace("  A ", "Added : ")
    SvnInfos.ChgPath = SvnInfos.ChgPath.replace("  D ", "Deleted : ")
    
    # Build Change Description
    for idx in range(MPathEndLine, revfdBufferCounts-1, 1):
        SvnInfos.ChgLog = SvnInfos.ChgLog + revfdBuffer[idx] + '\n'

    # Build Title
    for idx in range(0,revfdBufferCounts,1):
        regex = re.search('\[BIOS[0-9]{2}\]', revfdBuffer[idx])
        if regex != None:
            SvnInfos.ChgTitle = revfdBuffer[idx]
            break
    return

def mailcomposer_Text():
    global msg
    
    msg['Subject'] = SvnInfos.ChgTitle
    msg['From'] = SvnInfos.EmailSender
    msg['To'] = SvnInfos.EmailRecipientList

    text = "Revision: " + '\n'\
           + str(SvnInfos.Revision) + '\n'\
           + '\n'\
           + "Date: " + '\n'\
           + SvnInfos.Date + '\n' \
           + SvnInfos.ChgLog \
           + '----' + '\n' \
           + SvnInfos.ChgPath + '\n'\
           + "Modified by: " + SvnInfos.Author
    print text
    # Record the MIME types of both parts - text/plain and text/html.
    TextContext = MIMEText(text, 'plain')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(TextContext)
    
    return
    
def mailcomposer_HTML():
    global msg
    
    msg['Subject'] = SvnInfos.ChgTitle
    msg['From'] = SvnInfos.EmailSender
    msg['To'] = SvnInfos.EmailRecipientList

    body = "Revision: " + '\n'\
           + str(SvnInfos.Revision) + '\n'\
           + '\n'\
           + "Date: " + '\n'\
           + SvnInfos.Date + '\n' \
           + SvnInfos.ChgLog \
           + '----' + '\n' \
           + SvnInfos.ChgPath + '\n'\
           + "Modified by: " + SvnInfos.Author
    print body

    # Update Bold String
    body = body.replace("Revision:", "<b>Revision:</b>", 1)
    body = body.replace("Date:", "<b>Date:</b>", 1)
    body = body.replace("Story ID:", "<b>Story ID:</b>", 1)    
    body = body.replace("Story Description:", "<b>Story Description:</b>", 1)
    body = body.replace("Issue ID/Description:", "<b>Issue ID/Description:</b>", 1)
    body = body.replace("Root cause:", "<b>Root cause:</b>", 1)
    body = body.replace("Change Description:", "<b>Change Description:</b>", 1)
    body = body.replace("Repro Steps:", "<b>Repro Steps:</b>", 1)
    body = body.replace("Catalog:", "<b>Catalog:</b>", 1)
    body = body.replace("Does this apply to other projects?", "<b>Does this apply to other projects?</b>", 1)
    body = body.replace("Is Bios specification update required?", "<b>Is Bios specification update required?</b>", 1)
    body = body.replace("Is test plan update required?", "<b>Is test plan update required?</b>", 1)
    body = body.replace("File Changed:", "<b>File Changed:</b>", 1)
    body = body.replace("Modified by:", "<b>Modified by:</b>", 1)
    
    body = body.replace("\n", "<BR>")
    body_html = """\
            <html>
              <head></head>
              <body>
                <p style='font-family:"Calibri",sans-serif; font-size:12.0pt;'>
            """ + body + \
            """
                </font></p>
              </body>
            </html>
            """
    # Record the MIME types of both parts - text/plain and text/html.            
    HtmlContext = MIMEText(body_html, 'html')   
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred. 
    msg.attach(HtmlContext)
    return
    
def SendEmail():
    # Send the message via local SMTP server.
    EmailObj = smtplib.SMTP(SMTPServer,SMTPPort)
    
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    EmailObj.sendmail( SvnInfos.EmailSender,  SvnInfos.EmailRecipientList, msg.as_string())
    EmailObj.quit()
    return

def main():

    # To collect information of designated revision
    try:
        SvnInfoGrabber(sys.argv[1])
    except:
        print("Wrong revision as input, try again.")
 
      
    # Compose the email
    #mailcomposer_Text
    mailcomposer_HTML()

    # Send out notification
    SendEmail()

    return

if __name__ == '__main__':
    main()

