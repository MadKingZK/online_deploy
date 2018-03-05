#-*- coding: UTF-8 -*-
import paramiko
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

class ssh2(object):
    def __init__(self,hostname,port,username):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.pk_file = open('/root/.ssh/id_rsa','r')
        self.key = paramiko.RSAKey.from_private_key(self.pk_file)
        self.ssh.load_system_host_keys()

    def ssh_conn(self):
        self.ssh.connect(self.hostname,self.port,self.username,pkey=self.key)

    def handler(self,cmd):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            channle = stdout.channel
            status = channle.recv_exit_status()
            err = stderr.readlines()
            out = stdout.readlines()
            result={'status':status,'out':out,'err':err}
        except Exception as err:
            result={'status':1,'err':err}
        return result

    def custom_handle(self,commandstr):
        result = self.handler(commandstr)
        status = result.get('status')
        out = ''.join(result.get('out'))
        err = ''.join(result.get('err'))
        print('------>>>>>>>>>',status)
        if status == 0:
            return [True,out]
        else:return [False,err]

    def file_exists(self,file):
        result = self.handler('ls -d %s | wc -l'% file)
        out = result.get('out')
        #print '<><><><><><><><>',out
        if out is not None:
            if int(out[0].strip()) == 1:
                return [True,'file exists']
            else:
                return [False,''.join(result['out'])]
        else:
            return [False,''.join(result['err'])]

    def auto_deploy(self,cmd):
        result = self.handler(cmd)
        print result
        for i in result['out']:
            print i
        out = result.get('out')
        print 'out-------out--------out',out
        err = result.get('err')
        print 'err-------err--------err',err
        if out is not None:
            for o in out:
                if "BUILD SUCCESS" in o:
                    print '-------<><><--------<><><'
                    return [True,''.join(out)]
        else:
            return [False,''.join(err)]

    def ssh_close(self):
        self.ssh.close()

if __name__=='__main__':
    ssh = ssh2('192.168.1.1',22,'eng')

    res = ssh.custom_handle('ls')

