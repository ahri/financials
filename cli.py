#!/usr/bin/env python
# coding: utf-8
import cmd
from services import Service, Halifax
from config import load, save, _config, _get_passphrase

class ExitCmd(cmd.Cmd, object):
    def can_exit(self):
        return True

    def onecmd(self, line):
        r = super (ExitCmd, self).onecmd(line)
        if r and (self.can_exit() or
            raw_input('exit anyway ? (yes/no):')=='yes'):
                 return True
        return False

    def do_exit(self, s):
        return True

    def help_exit(self):
        print "Exit the interpreter."
        print "You can also use the Ctrl-D shortcut."

    do_EOF = do_exit
    help_EOF = help_exit

class ServiceCmd(ExitCmd):

    def __init__(self):
        super(ServiceCmd, self).__init__()
        self._services = []

    def do_list(self, s):
        print ", ".join([service.__name__ for service in Service.services()])

    def help_list(self):
        print "List supported services"

    def do_active(self, s):
        print ", ".join([s.__class__.__name__ for s in self._services])

    def help_active(self):
        print "List active services"

    def do_login(self, svc):
        """Login to a service"""
        self.login(svc)

    def login(self, svc, login_details=None):
        try:
            s = Service.service(svc)(login_details=login_details)
            self._services.append(s)
            print "[Status: %s]" % s.status()
        except ValueError as e:
            print e

    def do_autologin(self, s):
        load('config.enc')
        for svc in _config:
            if 'login_details' in _config[svc]:
                self.login(svc, login_details=_config[svc]['login_details'])

    def help_autologin(self):
        print "Automatically log in to all services saved in the config file"

    def do_savelogin(self, svc):
        try:
            d = {}
            for k in Service.login_reqs(svc):
                d[k] = _get_passphrase(prompt=k.title(), confirm=True, length_req=0)
            if svc not in _config:
                _config[svc] = {}
            _config[svc]['login_details'] = d
            save('config.enc')
        except ValueError as e:
            print e

    def help_savelogin(self):
        print "Save login details for a given service"

if __name__ == '__main__':
    interpreter = ServiceCmd()

    import sys
    from debug import debug_exceptions
    sys.excepthook = debug_exceptions

    interpreter.cmdloop()
