#!/usr/bin/env python
# coding: utf-8
import cmd
from services import Service, Halifax

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

    def do_login(self, service):
        """Login to a service"""

        try:
            s = Service.service(service)()
            self._services.append(s)
            print "[Status: %s]" % s.status()
        except ValueError as e:
            print e

if __name__ == '__main__':
    interpreter = ServiceCmd()

    import sys
    from debug import debug_exceptions
    sys.excepthook = debug_exceptions

    interpreter.cmdloop()
