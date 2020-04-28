import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Auto BIOS Newsgroup Requirement:
# 1. Need to have signature "[BIOS"
# 2. Need to Fill in the following items
Sender = 'neo.chou@hp.com'
Author = 'neo.chou'
#Recipient = ['neo.chou@hp.com']
Recipient = ['houprtcorebiosdevorg@hp.com', 'mobile.tw.bios.execution@hp.com', 'cmitmobilebiosprogrammanagers@hp.com', 'kuo.asia.all@hp.com', 'A32_Tiano@compal.com', 'MSI_CMIT_BIOS_team@msi.com', 'dm_bios@pegatroncorp.com', 'HPBNBQuanta@quantatw.com', 'ZZ_HP_CMIT_BIOS@tnitek.com', 'Ast01Swbios@wistron.com', 'fxn.bpc.bios@foxconn.com', 'IECSliceBIOS@inventec.com', '#IECBU1A1b225f@inventec.com']


def SendHpMail(title, context):
    msg = MIMEMultipart()
    msg['From'] = Sender
    msg['To'] = ", ".join(Recipient)
    msg['Subject'] = title
    msg.attach(context)
    server = smtplib.SMTP('smtp3.hp.com', 25)
    server.ehlo()
    server.sendmail(Sender, Recipient, msg.as_string())
    server.quit()
    print("    From: ", msg['From'])
    print("    To: ", msg['To'])
    print("    Subject: ", msg['Subject'])


def SendBiosNewsgroup(SvnRevision, SvnDate, SvnChangedPath, SvnMessage):
    SvnChangedPath = SvnChangedPath.replace("  M ", "Modified : ")
    SvnChangedPath = SvnChangedPath.replace("  A ", "Added : ")
    SvnChangedPath = SvnChangedPath.replace("  D ", "Deleted : ")
    while SvnMessage.find("\n\n\n") != -1:
        SvnMessage = SvnMessage.replace("\n\n\n", "\n\n")
    if SvnMessage.find("[BIOS") != -1:
        title = "[BIOS" + SvnMessage.split("[BIOS")[1].split("\n")[0]
        SvnMessage = SvnMessage.replace("Story ID:", "<b>Story ID:</b>", 1)
        SvnMessage = SvnMessage.replace("Story Description:", "<b>Story Description:</b>", 1)
        SvnMessage = SvnMessage.replace("Issue ID/Description:", "<b>Issue ID/Description:</b>", 1)
        SvnMessage = SvnMessage.replace("Root cause:", "<b>Root cause:</b>", 1)
        SvnMessage = SvnMessage.replace("Change Description:", "<b>Change Description:</b>", 1)
        SvnMessage = SvnMessage.replace("Repro Steps:", "<b>Repro Steps:</b>", 1)
        SvnMessage = SvnMessage.replace("Catalog:", "<b>Catalog:</b>", 1)
        SvnMessage = SvnMessage.replace("Does this apply to other projects?", "<b>Does this apply to other projects?</b>", 1)
        SvnMessage = SvnMessage.replace("Is Bios specification update required?", "<b>Is Bios specification update required?</b>", 1)
        SvnMessage = SvnMessage.replace("Is test plan update required?", "<b>Is test plan update required?</b>", 1)
        SvnMessage = SvnMessage.replace("Modified by:", "<b>Modified by:</b>", 1)
        SvnMessage = SvnMessage.replace("Reviewed by:", "<b>Reviewed by:</b>", 1)
        body = "<b>Revision:</b>\n" + SvnRevision + "\n\n<b>Date:</b>\n" + SvnDate + "\n\n" + SvnMessage + "\n<b>Files Modified:</b>\n" + SvnChangedPath
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
        context = MIMEText(body_html, 'html')
        SendHpMail(title, context)


def SvnLogFormat(CurrentRev, LatestRev):
    if (CurrentRev > LatestRev):
      return
    CmdResult = os.popen("svn log https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14 -v -r %d:%d" % (CurrentRev, LatestRev)).read()
    for RevResult in CmdResult.split("------------------------------------------------------------------------"):
        if (RevResult.find("Changed paths:") == -1):
            continue;
        SvnRevision = RevResult.split("\n")[1].split(" | ")[0].split("r")[1]
        SvnAuthor = RevResult.split("\n")[1].split(" | ")[1]
        SvnDate = RevResult.split("\n")[1].split(" | ")[2].split(" ")[0]
        SvnChangedPath = RevResult.split("Changed paths:\n")[1].split("\n\n")[0]
        SvnMessage = RevResult.split("Changed paths:\n")[1].split("\n\n", 1)[1]
#        print(">>>>>>>>>>>>>>>>>>>>>>>>>>")
#        print("SvnRevision: \n" + SvnRevision)
#        print("SvnAuthor: \n" + SvnAuthor)
#        print("SvnDate: \n" + SvnDate)
#        print("SvnChangedPath: \n" + SvnChangedPath)
#        print("SvnMessage: \n" + SvnMessage)
#        print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if (SvnAuthor == Author):
            print("  Send newsgroup for SVN r%d" % CurrentRev)
            SendBiosNewsgroup(SvnRevision, SvnDate, SvnChangedPath, SvnMessage)


def ReadFileRev():
    fin = open("SvnRevFile.txt", "r")
    rev = int(fin.read())
    fin.close()
    return rev


def WriteFileRev(rev):
    fout = open("SvnRevFile.txt", "w")
    fout.write(str(rev))
    fout.close()


def LatestSvnRev():
    CmdResult = os.popen("svn info https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14").read()
    try:
        SvnRevision = CmdResult.split("Revision: ")[1].split("\n")[0]
    except:
        SvnRevision = -1
    return int(SvnRevision)


def main():
    now = datetime.now()
    print("%s/%s/%s %s:%s:%s:" % (now.year, now.month, now.day, now.hour, now.minute, now.second))
    OriginalRev = ReadFileRev()
    CurrentRev = OriginalRev + 1
    LatestRev = LatestSvnRev()
    if (LatestRev == -1):
        print("  Svn get LatestRev fail.")
        return -1
    SvnLogFormat(CurrentRev, LatestRev)
    if (LatestRev != OriginalRev):
        WriteFileRev(LatestRev)
        print("  Update Revision to %d" % LatestRev)
    else:
        print("  No updated.")


main()
