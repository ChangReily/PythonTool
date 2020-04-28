import os
import pysvn
def ssl_server_trust_prompt( trust_dict ):
    return (True    # server is trusted
           ,trust_dict["failures"]
           ,True)   # save the answer so that the callback is not called again

client = pysvn.Client()
client.exception_style = 1
client.callback_ssl_server_trust_prompt = ssl_server_trust_prompt
URL_Path = 'https://csvnaus-pro.austin.hpicorp.net:20181/svn/svn-psgfw-platform14/trunk/Projects/BIOS17Smr/HpBasso'

client = pysvn.Client()


SvnRevision = pysvn.Revision(pysvn.opt_revision_kind.number, 94691)

#client.checkout(URL_Path,'D:\Test\94691',recurse=True, revision=SvnRevision, peg_revision=SvnRevision, ignore_externals=True)

props  = client.propget('svn:externals', 'D:\Test\94691')


prop_names = sorted( props.keys() )
for name in prop_names:
    #print( '%s: %s' % (name, props[name]) )
    print( '%s\n' % (name) )
    if 'svn-psgfw-platform14' in props[name]:
        print 'delprop'
    else :
        print( '%s' % (props[name]) )
