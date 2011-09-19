# coding: utf-8
import inspect
import re
from copy import copy
from getpass import getpass
from pycurlbrowser.browser import Browser

class Service(object):

    """
    The basic representation of an service, containing any common stuff
    """

    def __init__(self, login_details=None):
        self.browser = Browser()

        # replace Browser.go
        self._go = self.browser.go
        self.browser.go = self.go_replacement

        if login_details is not None:
            self.login(**login_details)
        else:
            self.login_interactive()

    def login_interactive(self):
        login_details = {}
        for r in self.login_reqs(self.__class__.__name__):
            login_details[r] = getpass("%s: " % r.replace('_', ' ').title())
        self.login(**login_details)

    def go_replacement(self, url):
        """Replacement for Browser.go()"""
        if self.browser.url == url:
            return

        res = self._go(url)
        assert res == 200, "Only handle valid results"

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

    def login(self, username, password, secret):
        """Called at init if login details supplied, otherwise called via login()"""
        self.username = username
        self.password = password
        self.secret = secret

        b = self.browser
        b.go('https://www.halifax-online.co.uk/personal/logon/login.jsp')

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

class Santander(Service):

    """
    Represent Santander Credit Card UK
    """

    def login(self, card_number, internet_id, security_number):
        b = self.browser
        b.go('https://myonlineaccounts3.abbeynational.co.uk/GPCC_ENS/BtoChannelDriver.ssobto?dse_operationName=StartL2')
        b.form_select('form1')
        b.form_data_update(card=card_number, usuario=internet_id, password=security_number)
        b.form_submit('Log on')
        self.main_content_url = b.xpath('//frame[@title="Main Content"]')[0].get('src')
        b.go(self.main_content_url)

    def status(self):
        return "Balance: £%(balance).2f, Due: %(payment_due)s" % dict(balance=self.balance()/100.0,
                                                                      payment_due=self.payment_due())

    def balance(self):
        self.browser.go(self.main_content_url)
        return int(self.browser.xpath('//div[@class="html"]/div[@class="f-salida lateral01"]//div[@class="fila"]/span/text()')[0].replace(u'\xa3 ', '').replace('.', ''))

    def payment_due(self):
        self.browser.go(self.main_content_url)
        return self.browser.xpath('//div[@class="html"]/div[@class="f-salida lateral01"]//div[@class="fila"]/span/text()')[2] # TODO: make this a date obj

class Tmobile(Service):

    """
    Represent T-Mobile UK
    """

    def login(self, username, password):
        b = self.browser
        b.go('http://www.t-mobile.co.uk/service/your-account/mtm-user-login-dispatch/')

        b.form_select('MTMUserLoginForm')
        b.form_data_update(username=username, password=password)
        b.form_submit()

    def mins_left(self):
        self.browser.go('https://www.t-mobile.co.uk/service/your-account/private/load-unbilled-use-data/')
        return re.search('([0-9:]*) Minutes', self.browser.src).group(1)

    def next_bill(self):
        self.browser.go('https://www.t-mobile.co.uk/service/your-account/private/load-unbilled-use-data/')
        return re.search('Items will be billed on ([0-9/]*)', self.browser.src).group(1) # TODO: make this a date obj

    def unbilled_usage(self):
        self.browser.go('https://www.t-mobile.co.uk/service/your-account/private/load-unbilled-use-data/')
        return int(re.search('([0-9\.]*)</em> activity since your last bill', self.browser.src).group(1).replace('.', ''))

    def status(self):
        return "Mins left: %(mins_left)s until %(next_bill)s, unbilled: £%(unbilled_usage).2f" % dict(mins_left=self.mins_left(),
                                                                                                    next_bill=self.next_bill(),
                                                                                                    unbilled_usage=self.unbilled_usage()/100.0)
