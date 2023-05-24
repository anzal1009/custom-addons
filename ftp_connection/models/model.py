import json
from odoo import api, models, fields, _
import requests
from ftplib import FTP
import pysftp
import os
import sys
import errno



class AccountFtpInherit(models.Model):
    _inherit = 'account.move'


    def action_ftp_connection(self):

        for rec in self:
            rec.ref = "new"


        # print("yess")

        # # Set connection object to None (initial value)
        # connection = None
        # hostname = "165.22.223.124"
        # username = "root"
        # password = "!V@C6rgR9Vh"
        # port = "22"
        #
        # # def connect(self):
        # try:
        #     # Get the sftp connection object
        #     self.connection = pysftp.Connection(
        #         host= hostname,
        #         username= username,
        #         password= password,
        #         port= port,
        #     )
        # except Exception as err:
        #     raise Exception(err)
        # finally:
        #     print(f"Connected to ")


        #
        # class Sftp:
        #     def __init__(self, hostname, username, password, port=22):
        #         """Constructor Method"""
        #         # Set connection object to None (initial value)
        #         self.connection = None
        #         self.hostname = hostname
        #         self.username = username
        #         self.password = password
        #         self.port = port
        #
        #     def connect(self):
        #         """Connects to the sftp server and returns the sftp connection object"""
        #
        #         try:
        #             # Get the sftp connection object
        #             self.connection = pysftp.Connection(
        #                 host=self.hostname,
        #                 username=self.username,
        #                 password=self.password,
        #                 port=self.port,
        #             )
        #         except Exception as err:
        #             raise Exception(err)
        #         finally:
        #             print(f"Connected to {self.hostname} as {self.username}.")
        #
        #     def disconnect(self):
        #         """Closes the sftp connection"""
        #         self.connection.close()
        #         print(f"Disconnected from host {self.hostname}")
        #
        #







        #
        # # FTP connection details
        # ftp_host = 'ftp.example.com'
        # ftp_user = 'your_username'
        # ftp_password = 'your_password'
        # ftp_directory = '/path/to/folder/'
        #
        # # Establish FTP connection
        # ftp = FTP(ftp_host)
        # ftp.login(user=ftp_user, passwd=ftp_password)
        #
        # # Change to the desired directory
        # ftp.cwd(ftp_directory)
        #
        # # List all files in the directory
        # file_list = ftp.nlst()
        #
        # # Loop through each file and print its name
        # for file_name in file_list:
        #     print(file_name)
        #
        # # Close the FTP connection
        # ftp.quit()



#
# import pysftp
#
# with pysftp.Connection('hostname', username='me', password='secret') as sftp:
#
#     with sftp.cd('/allcode'):           # temporarily chdir to allcode
#         sftp.put('/pycode/filename')  	# upload file to allcode/pycode on remote
#         sftp.get('remote_file')         # get a remote file