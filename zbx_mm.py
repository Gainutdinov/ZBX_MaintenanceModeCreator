#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import base64
import urllib.request
import urllib.parse
import requests
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from shell_ui import Ui_MainWindow
from cred_shell_ui import Ui_Dialog

class CredDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(CredDialog, self).__init__(parent)
        #super().__init__()
        #QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        #self.btnButton.setDisable(True)
        self.ui.lineEdit.textChanged.connect(self.disableButton)
        self.ui.lineEdit_2.textChanged.connect(self.disableButton)
        self.ui.lineEdit_3.textChanged.connect(self.disableButton)

    def disableButton(self):
        if len(self.ui.lineEdit.text()) > 0 and len(self.ui.lineEdit_2.text()) > 0 and len(self.ui.lineEdit_3.text()) > 0:
            self.ui.buttonBox.setEnabled(True)


class MyWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWin, self).__init__(parent)
        #super().__init__()
        #QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        with open('zbx_info.json') as json_file:  
            data = json.load(json_file)
            self.user = base64.b64decode((data['username']).encode('UTF-8')).decode('ascii')
            self.password = base64.b64decode((data['password']).encode('UTF-8')).decode('ascii')
            self.zabbixUrl = base64.b64decode((data['serverUrl']).encode('UTF-8')).decode('ascii') + "/zabbix/api_jsonrpc.php"

        now = QDateTime.currentDateTime()
        tomorrow = QDateTime.currentDateTime().addDays(1)

        self.ui.name_le.setText('Maintenance mode created by ' + self.user + ' - ' + QDateTime.currentDateTime().toString(Qt.ISODate))
        self.ui.dscr_le.setText(self.user + ' put here your description')
        #self.ui.dscr_le.setText('Please feel free to delete when its expires')

        self.headers = {'Content-type':'application/json'}
        self.payload = {"jsonrpc":"2.0", "method":"user.login","params":{"user":self.user,"password":self.password},"id":0,"auth":None}
        self.ui.pushButton.clicked.connect(self.PushFunction)
        #self.ui.finishDateTime_dte.setDate(QDate.currentDate())
        self.ui.startDateTime_dte.setDateTime(now)
        self.ui.finishDateTime_dte.setDateTime(tomorrow)
        self.startMonitoring()


    def startMonitoring(self):
        r = requests.post(self.zabbixUrl, data=json.dumps(self.payload),headers=self.headers, verify=False)
        if 'result' in r.json():
            self.token=(r.json())['result']
            #print(self.token)
            self.ui.textEdit.insertPlainText('token is {0}\n'.format(self.token))
        else:
            self.ui.textEdit.insertPlainText('NOO')
        self.ui.textEdit.insertPlainText('---------------------------\n')

        r = requests.post(self.zabbixUrl, data=json.dumps({"jsonrpc": "2.0","method": "host.get","params":{}, "auth": self.token,"id": 1}),headers=self.headers, verify=False)
        # hostid name maintenance_status
        for host in (r.json())['result']:
            #print(host['name'],host['hostid'],host['maintenance_status'])
            item = QListWidgetItem(host['name'])
            #print(type(host['maintenance_status']))
            if (host['maintenance_status']!='0'):
                item.setBackground(QColor(255, 153, 0))
            data = (host['hostid'],host['maintenance_status'])
            item.setData(Qt.UserRole, data)
            self.ui.listWidget.addItem(item)


    def PushFunction(self):
        #print(self.ui.finishDateTime_dte.dateTime().toSecsSinceEpoch())
        startUnixTime=self.ui.startDateTime_dte.dateTime().toSecsSinceEpoch()
        finishUnixTime=self.ui.finishDateTime_dte.dateTime().toSecsSinceEpoch()
        period=finishUnixTime-startUnixTime
        if (self.ui.radioButton_2.isChecked()):
            maintenanceType=0 # with data collection
        else:
            maintenanceType=1 # with no data collection

        hostsToMM=[]
        if (self.ui.listWidget_2.count()):
            for _ in range(self.ui.listWidget_2.count()):
                usrRole=self.ui.listWidget_2.item(_).data(Qt.UserRole)
                hostsToMM.append(usrRole[0])
        self.ui.textEdit.insertPlainText(str(hostsToMM)+'\n')
        payload={"jsonrpc": "2.0","method": "maintenance.create", "params": {"name": self.ui.name_le.text(),"description":self.ui.dscr_le.text(),"maintenance_type": maintenanceType,"active_since": startUnixTime,"active_till": finishUnixTime,\
                "hostids": [\
                    "0"\
                ],\
                "timeperiods": [{"timeperiod_type": 0,"start_date":startUnixTime,"period": period}]},"auth": self.token,"id": 1}
        (payload['params'])['hostids']=hostsToMM
        #print(payload)
        r = requests.post(self.zabbixUrl, data=json.dumps(payload),headers=self.headers, verify=False)
        self.ui.textEdit.insertPlainText('------'+str(r)+'------')


             

if __name__=='__main__':
    # check whther file with credentials exists
    if not (os.path.isfile('./zbx_info.json')):
        #print("./zbx_info.json doesn't exist ")
        app = QApplication([])
        w = CredDialog()
        w.show()
        app.exec()
        if len(w.ui.lineEdit.text()) > 0 and len(w.ui.lineEdit_2.text()) > 0 and len(w.ui.lineEdit_3.text()) > 0:
            username=base64.b64encode((w.ui.lineEdit.text()).encode('UTF-8')).decode('ascii')
            password=base64.b64encode((w.ui.lineEdit_2.text()).encode('UTF-8')).decode('ascii')
            serverUrl=base64.b64encode((w.ui.lineEdit_3.text()).encode('UTF-8')).decode('ascii')
            data = { "username": username, "password": password, "serverUrl": serverUrl }
            with open('zbx_info.json', 'w') as f:
                json.dump(data, f)
            app1 = QApplication([])
            win = MyWin()
            win.show()
            app1.exec()
    else:
        app = QApplication([])
        win = MyWin()
        win.show()
        app.exec()

