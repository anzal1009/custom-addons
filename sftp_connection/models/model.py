from odoo import models, fields, api
import paramiko
# import pysftp
import pandas as pd
import base64
# import cx_Oracle
import collections
import requests
import json
import qrcode
from odoo import tools
import base64
from io import BytesIO
from datetime import datetime

from ftplib import FTP
import io
import pandas as pd


class AccountJournal(models.Model):
    _inherit = 'account.move'

#################################### FTP Connection ##############################
    def button_ftp_connection(self):
        print("helloo FTP")

        # FTP connection information
        hostname = '165.22.223.124'
        port = '22'
        username = 'root'
        password = '!V@C6rgR9Vh'

        # Remote file path
        remote_filepath = "/opt/EasternIRNTest/MTR_EXP.xlsx"

        # Establish an FTP connection
        ftp = FTP()
        ftp.connect(hostname, port)
        ftp.login(username, password)

        # Download the Excel file to a memory buffer
        buffer = io.BytesIO()
        ftp.retrbinary('RETR ' + remote_filepath, buffer.write)
        buffer.seek(0)

        # Read the Excel file using pandas
        df = pd.read_excel(buffer)

        # Print the contents row by row
        for index, row in df.iterrows():
            print(row)

        # Close the FTP connection
        ftp.quit()



########################################## SFTP Connection ##########################################


    # button
    def button_sftp_connection(self):
        print("Hiiii")
        self.retrieve_data_from_sftp()


    def retrieve_data_from_sftp(self):
        # SFTP connection details
        hostname = '165.22.223.124'
        port = '22'
        username = 'root'
        password = '!V@C6rgR9Vh'

        # Path to the Excel file on the remote system
        remote_path = "/opt/EasternIRNTest/MTR_EXP.xlsx"

        # Establish SSH/SFTP connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, port, username, password)

        # Open SFTP session
        sftp_client = ssh_client.open_sftp()

        # Download the Excel file to a temporary local file
        local_path = "/opt/EasternIRNTest/TEMP_MTR_EXP.xlsx"
        sftp_client.get(remote_path, local_path)

        # Read the Excel file using pandas
        df = pd.read_excel(local_path)
        for index, row in df.iterrows():
            print(row)

        # for row in df:
            # print(row)
            # print(row.INVOICE_NUM)
            # print(row.ODOO_STATUS)
            invoice_obj = self.env['account.move'].search([('name','=',row.INVOICE_NUM)])
            if not invoice_obj:
                if(row.HL_CITY == None):
                    HL_CITY = ","
                else:
                    HL_CITY = row.HL_CITY

                if (row.HL_ADDRESS3 == None):
                    HL_ADDRESS3 = ","
                else:
                    HL_ADDRESS3 = row.HL_ADDRESS3

                if (row.HL_ADDRESS4 == None):
                    HL_ADDRESS4 = ","
                else:
                    HL_ADDRESS4 = row.HL_ADDRESS4

                EXPORTERS_REF = row.EXPORTERS_REF
                invoice_dict = {
                    # 'type': 'out_invoice',
                    'move_type': 'out_invoice',
                    'name': row.INVOICE_NUM,
                    'documentdate': datetime.strptime(EXPORTERS_REF, '%d-%b-%Y').strftime('%d/%m/%Y'),
                    'documentnumber': row.INVOICE_NUM,
                    'documenttypecode': "INV",
                    'supplytypecode': "EXPWP",
                    'recipientlegalname': row.HP_PARTY_NAME,
                    'recipienttradename': row.HP_PARTY_NAME,
                    'recipientgstin': "URP",
                    'placeofsupply': "96",


                    'recipientaddress1': str(row.HL_ADDRESS1) +','+ str(row.HL_ADDRESS2) +',',
                    # 'recipientaddress2': row.HL_ADDRESS3 or +',' +','+ row.HL_ADDRESS4 or +',' +','+ row.HL_CITY or False ,
                    'recipientaddress2': str(HL_ADDRESS3) +','+ str(HL_ADDRESS4) +','+ str(HL_CITY) or +',',

                    'recipientplace': row.HL_ADDRESS3 ,
                    'recipientstatecode': "96",
                    'recipientpincode': "999999",
                    'slno': "",


                    'itemdescription': row.DESCRIPTION,
                    'istheitemagood': "G",
                    'hsnorsaccode': row.HSN_CODE,
                    'quantity': row.QTY_IN_KGS,
                    'unitofmeasurement': "KGS",
                    'itemprice': (row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR) / row.QTY_IN_KGS,
                    'grossamount': row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR,
                    'itemdiscountamount': row.DISCOUNT_VALUE_IN_INR,
                    'itemtaxablevalue': row.NETVALUE_IN_INR,
                    'gstrate': row.IGST_RATE,
                    'igstamount': row.IGST_PAYABLE,
                    'itemtotalamount': row.NETVALUE_IN_INR + row.IGST_PAYABLE,
                    'totaltaxablevalue': row.NETVALUE_IN_INR,
                    'igstamounttotal': row.IGST_PAYABLE,

                    'totalinvoicevalueininr': row.NETVALUE_IN_INR or row.IGST_PAYABLE,
                    'supplierlegalname': "Eastern Condiments Pvt. Ltd",
                    'gstinofsupplier': row.GSTIN,
                    'supplieraddress1': str(row.ADDRESS_LINE_1) + str(row.ADDRESS_LINE_2) + str(row.ADDRESS_LINE_3) + str(row.LOC_INFORMATION14) + str(row.LOC_INFORMATION15),
                    'supplierplace': row.LOC_INFORMATION15,
                    'supplierstatecode': "32",
                    'supplierpincode': row.POSTAL_CODE,
                    'typeofexport': "EXPWP",
                    'shippingportcode': "INCOK1",
                    'shippingbillnumber': "",
                    'shippingbilldate': "",
                    'shiptolegalname': "India Gateway Terminal Private Limited",
                    'shiptotradename': "India Gateway Terminal Private Limited",
                    'shiptogstin': "URP",
                    'shiptoaddress1': "Administration Building, ICTT,",
                    'shiptoaddress2': "Vallarpadam SEZ, Mulavukadu Village",
                    'shiptoplace': "Ernakulam",
                    'shiptopincode': "682504",
                    'shiptostatecode': "32",

                    #for bill generation

                    'transmode': row.SHIP_METHOD_MEANING,
                    'poreferencenumber': row.CUST_PO_NUMBER,
                    'poreferencedate': row.PO_DATE,
                    'cerno': row.ERC_NO,
                    'cinno': row.CIN,
                    'panno': row.PAN_NO,
                    'iecodeno': row.IE_CODE_NO,
                    'lutno': "AD320222011128W dtd 28/02/2022",
                    'vesselflightno': row.VESSEL_FLIGHT_NO,
                    'portofloading': row.PORT_OF_LOADING,
                    'portofdischarge': row.PORT_OF_DIS,
                    'countryoforigin': row.COUNTRY_OF_ORGN,
                    'countryoffdest': row.COUNTRY_OF_FDEST,
                    'termofdelpmnt': row.TERM_DEL_PMNT,
                    'findest': row.FIN_DEST,
                    'noofpkgs': row.NO_K_OF_PKGS,
                    'buyerothcons' : row.BUYER_OTH_CONS,

                }

                invoice_obj = self.env['account.move'].create(invoice_dict)
            duplicate_product = self.env['account.move.line'].search([('itemdescription','=',row.DESCRIPTION),('move_id','=',invoice_obj.id)])
            print(duplicate_product,"duplicate product")
            if not duplicate_product:
                product_line_dict = {
                    'name': row.DESCRIPTION,
                    'list_price': row.NETVALUE_IN_INR,
                }
                product_created = self.env['product.template'].create(product_line_dict)
                product_variant = self.env['product.product'].search([('product_tmpl_id', '=', product_created.id)])
                print(product_variant, "product tmpl")
                invoice_move_line_dict = {
                    'product_id': product_variant.id,
                    'move_id': invoice_obj.id,
                    'account_id': 7,

                    'linenumber': row.LINE_NUMBER,
                    'itemdescription': row.DESCRIPTION,
                    'istheitemagood': "G",
                    'hsnorsaccode': row.HSN_CODE,
                    'quantity': row.QTY_IN_KGS,
                    'unitofmeasurement': "KGS",
                    'itemprice': (row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR) / row.QTY_IN_KGS,
                    'grossamount': row.NETVALUE_IN_INR + row.DISCOUNT_VALUE_IN_INR,
                    'itemdiscountamount': row.DISCOUNT_VALUE_IN_INR,
                    'itemtaxablevalue': row.NETVALUE_IN_INR,
                    'gstrate': row.IGST_RATE,
                    'igstamount': row.IGST_PAYABLE,
                    'itemtotalamount': row.NETVALUE_IN_INR + row.IGST_PAYABLE,
                    'totaltaxablevalue': row.NETVALUE_IN_INR,
                    'igstamounttotal': row.IGST_PAYABLE,

                    'dispercent' : row.DISCOUNT_PER,
                    'qtyinctn' : row.QTY_IN_CTN,
                    'amtinusd' : row.AMT,
                    # 'amtinusd' : row.NETVALUE_IN_USD,
                    'netamtinusdfob' : row.NETVALUE_IN_USD,
                    'rateperkgusd' : row.RATE_PER_KG,
                }
                invoice_line_created = self.env['account.move.line'].create(invoice_move_line_dict)

                #
                #
                # pulled_data.append(row.INVOICE_NUM)
                #
                # print(pulled_data)
            # connection.close()
            # updatecursor = connection.cursor()
            # cursor.execute('UPDATE XXEST_EXPORT_EINVOICE SET ODOO_STATUS = 1')
            # connection.commit()
            # print(updatecursor)
        # df.execute('UPDATE XXEST_EXPORT_EINVOICE SET ODOO_STATUS = 1')
        # connection.commit()
        # print("updatedsplit")
        #
        # Print the contents of the Excel file
        # print(df)

        # Close the SFTP session and SSH connection
        sftp_client.close()
        ssh_client.close()

