#import pandas as pd

class HelloWorld:
    _reg_clsid_ = '{E4AB613F-EB96-44C4-AFEF-0DF74BD61D06}'

    _reg_desc_ = "Python Test COM Server"

    _reg_progid_ = "Python.TestServer"

    _public_methods_ = ['Hello']

    _public_attrs_ = ['noCalls']

    _readonly_attrs_ = ['noCalls']

    def __init__(self):
        self.noCalls = 0

    def Hello(self):
        self.noCalls = self.noCalls + 1
        return "Hello World"


if __name__=='__main__':
    import win32com.server.register
    win32com.server.register.UseCommandLine(HelloWorld)