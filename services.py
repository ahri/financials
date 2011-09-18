# coding: utf-8
import inspect
from copy import copy
from getpass import getpass
from pycurlbrowser.browser import Browser

class Service(object):

    """
    The basic representation of an service, containing any common stuff
    """

    def __init__(self, initial_url, login_details=None):
        self.browser = Browser(initial_url)
        if login_details is not None:
            self.login(**login_details)
        else:
            self.login_interactive()

    def login_interactive(self):
        login_details = {}
        for r in self.login_reqs(self.__class__.__name__):
            login_details[r] = getpass("%s: " % r.title())
        self.login(**login_details)

    def go_if_not_there(self, url):
        if self.browser.url == url:
            return

        self.browser.go(url)

    @classmethod
    def services(cls):
        for c in (v for v in copy(globals()).values() if inspect.isclass(v)):
            if c == Service:
                continue
            if cls in inspect.getmro(c):
                yield c

    @classmethod
    def service(cls, name):
        for service in cls.services():
            if service.__name__ == name:
                return service

        raise ValueError("No supported service named '%s'" % name)

    @classmethod
    def login_reqs(cls, svc_name):
        return inspect.getargspec(cls.service(svc_name).login).args[1:]

class Halifax(Service):

    """
    Represent Halifax (HBOS) UK
    """

    def __init__(self, **kwargs):
        super(Halifax, self).__init__('https://www.halifax-online.co.uk/personal/logon/login.jsp', **kwargs)

    def login(self, username, password, secret):
        """Called at init if login details supplied, otherwise called via login()"""
        self.username = username
        self.password = password
        self.secret = secret

        b = self.browser

        b.form_select('frmLogin')
        b.form_data_update(**{'frmLogin:strCustomerLogin_userID': self.username,
                              'frmLogin:strCustomerLogin_pwd': self.password})

        b.form_submit_no_button()
        b.form_select('frmentermemorableinformation1')

        for d in b.form_dropdowns_nodes:
            idx = int(d.label.text.replace("Character ", "").replace(u" \xa0", ""))
            b.form_fill_dropdown(d.name, u"\xa0" + self.secret[idx-1])

        b.form_submit_no_button()

    def balance(self):
        """Balance for account"""
        return self.browser.xpath('//p[@class="balance"]/text()')[0]

    def status(self):
        return self.balance()
