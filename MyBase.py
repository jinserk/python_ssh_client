#!/usr/bin/python
###########################################################################
#
#   MyBase.py
#       base class definition
#
#   Jinserk Baik <jinserk.baik@gmail.com>
#
#   This source code is distributed under BSD License.
#   The use of this code implies you agree the license.
#
#   Copyright (c) 2013, Jinserk Baik All rights reserved.
#
###########################################################################


import sys, cgitb
import datetime as dt


def _catch_errors():
    sys.excepthook = _my_except_hook


def _my_except_hook(etype, evalue, etraceback):
    _do_verbose_exception((etype, evalue, etraceback))


def _do_verbose_exception(exc_info=None):
    if exc_info is None:
        exc_info = sys.exc_info()

    txt = cgitb.text(exc_info)

    d = dt.datetime.now()
    p = (d.year, d.month, d.day, d.hour, d.minute, d.second)        
    filename = "ErrorDump-%d%02d%02d-%02d%02d%02d.txt" % p

    open(filename,'w').write(txt)
    print "** EXITING on unhandled exception - See %s" % filename  
    sys.exit(1)




class MyBase:

    def __init__(self, debug=False):
        self._debug_flag = debug


    def __del__(self):
        pass


    def _debug(self, *args):
        if self._debug_flag:
            try:
                print ' '.join(args)
            except Exception as e:
                print args




if __name__ == '__main__':
    pass

