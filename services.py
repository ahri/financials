# coding: utf-8
import inspect
from copy import copy
from getpass import getpass
from pycurlbrowser.browser import Browser

class Service(object):

    """
    The basic representation of an service, containing any common stuff
    """

    def __init__(self, initial_url):
        self.browser = Browser(initial_url)
        self.login()

    @classmethod
    def services(cls):
        for c in (v for v in copy(globals()).values() if inspect.isclass(v)):
            if c == cls:
                continue
            if cls in inspect.getmro(c):
                yield c

    @classmethod
    def service(cls, name):
        for service in cls.services():
            if service.__name__ == name:
                return service

        raise ValueError("No supported service named '%s'" % name)

class Halifax(Service):

    """
    Represent Halifax (HBOS) UK
    """

    def __init__(self):
        super(Halifax, self).__init__('https://www.halifax-online.co.uk/personal/logon/login.jsp')

    def login(self):
        """Called at init"""
        self.USERNAME = raw_input("Username: ")
        self.PASSWORD = getpass("Password: ")
        self.SECRET = getpass("Secret: ")

        b = self.browser

        b.form_select('frmLogin')
        b.form_data_update(**{'frmLogin:strCustomerLogin_userID': self.USERNAME,
                              'frmLogin:strCustomerLogin_pwd': self.PASSWORD})

        b.form_submit_no_button()
        b.form_select('frmentermemorableinformation1')

        for d in b.form_dropdowns_nodes:
            idx = int(d.label.text.replace("Character ", "").replace(u" \xa0", ""))
            b.form_fill_dropdown(d.name, u"\xa0" + self.SECRET[idx-1])

        b.form_submit_no_button()

    def balance(self):
        """Balance for account"""
        return self.browser.xpath('//p[@class="balance"]/text()')[0]

    def status(self):
        return self.balance()
