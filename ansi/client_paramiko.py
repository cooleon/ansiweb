# coding:utf8
import paramiko

class ParamikoClient(object):
    def __init__(self,db_obj):
        #self.config = configparser.ConfigParser()
        #self.config = configparser.RawConfigParser()
        #self.config.read(config_str)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp_client = None
        self.client_state = 0
    def connet(self):
        try:
            self.client.connect(hostname=db_obj.hostip,
                           port=db_obj.port,
                           username=db_obj.username,
                           password=db_obj.password,
                           timeout=30)
            self.client_state = 1
        except Exception,e:
            print e
            try:
                self.client.close()
            except:
                pass
    def run_command(self,cmd_str):
        if self.client_state == 0:
            self.connet()
        try:
            stdin,stdout,stderr = self.client.exec_command(cmd_str,timeout=5)
        except Exception,e:
            print e
            try:
                self.client.close()
            except:
                pass
        else:
            return stdout.readlines()

    # def get_sftp_client(self):
    #     if self.client_state == 0:
    #         self.connet()
    #
    #     if not self.sftp_client:
    #         self.sftp_client = paramiko.SFTPClient.from_transport(self.client.get_transport())
    #     return self.sftp_client
