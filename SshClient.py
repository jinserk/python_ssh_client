#!/usr/bin/python
###########################################################################
#
#   SshClient.py
#       base client class for remote SSH server
#
#   Jinserk Baik <jinserk.baik@gmail.com>
#   
#   This source code is distributed under BSD License.
#   The use of this code implies you agree the license.
#
#   Copyright (c) 2013, Jinserk Baik All rights reserved.
#
###########################################################################

import sys, os, select
import os.path as op
import posixpath as pp
import paramiko as pm
import glob as gb
import SshGlob as sgb
from MyBase import MyBase, MyError

MAX_BUF_SIZE = 8192
TIMEOUT = 0.5

def _eintr_retry(func, *args):
    """restart a system call interrupted by EINTR.
       this function is referred from SocketServer.py in the stdlib."""
    while True:
        try:
            return func(*args)
        except (OSError, select.error) as e:
            if e.args[0] != errno.EINTR:
                raise

class SshClient(MyBase):

    defaultkeyfile = '~/.ssh/id_rsa'

    def __init__(self):
        MyBase.__init__(self, debug=False)
        self.client = pm.SSHClient()
        self.client.set_missing_host_key_policy(pm.AutoAddPolicy())

    def connect(self, host, userid, password=None, keyfile=None):
        try:
            if password != None:
                self.client.connect(host, username=userid, password=password)
            else:
                key = self._prepare_key(keyfile)
                self.client.connect(host, username=userid, pkey=key)
        except Exception as e:
            self._debug(e)
            print 'connection is failed. please check your remote settings.'
            sys.exit(1)

    def _prepare_key(self, keyfile):
        if keyfile == None:
            keyfile = self.defaultkeyfile
        keyfile = op.abspath(op.expanduser(keyfile))
        if not op.exists(keyfile):
            raise MyError('private key file not found')
        return pm.RSAKey.from_private_key_file(keyfile)

    def command(self, *args):
        tr = self.client.get_transport()
        #tr.set_keepalive(1)
        ch = tr.open_session()
        ch.get_pty()
        ch.set_combine_stderr(True)
        cmd = ' ; '.join(args)
        ch.exec_command(cmd)
        while not ch.exit_status_ready():
            r, w, e = _eintr_retry(select.select, [ch], [], [], TIMEOUT)
            if ch in r:
                msg = ch.recv(MAX_BUF_SIZE).strip('\n')
                if msg != '':
                    print msg

    def write(self, filename, data):
        sftp = self.client.open_sftp()
        sftp.open(self.convertPath(filename), 'w').write(data)

    def read(self, filename):
        sftp = self.client.open_sftp()
        data = sftp.open(self.convertPath(filename), 'r').read()
        return data

    def put(self, lfiles, rdir):
        lfs = gb.glob(lfiles)
        rdir = self.convertPath(rdir)
        sftp = self.client.open_sftp()
        if len(lfs) > 0:
            self.checkRemotePath(sftp, rdir)
            print 'put local:{:}'.format(lfiles),\
                  '-> remote:{:}'.format(rdir)
        for lf in lfs:
            if not op.isdir(lf):
                rf = pp.join(rdir, op.basename(lf))
                sftp.put(lf, rf)
                sftp.chmod(rf, os.stat(lf).st_mode)

    def get(self, rfiles, ldir):
        sftp = self.client.open_sftp()
        rfiles = self.convertPath(rfiles)
        rfs = sgb.glob(sftp, rfiles)
        if len(rfs) > 0:
            self.checkLocalPath(ldir)
            print 'get remote:{:}'.format(rfiles),\
                  '-> local:{:}'.format(ldir)
        for rf in rfs:
            if not sgb.isdir(sftp, rf):
                lf = op.join(ldir, pp.basename(rf))
                sftp.get(rf, lf)
                os.chmod(lf, sftp.stat(rf).st_mode)

    def remove(self, files):
        sftp = self.client.open_sftp()
        rfs = sgb.glob(sftp, files)
        for rf in rfs:
            if not sgb.lexists(sftp, rf):
                continue
            if sgb.isdir(sftp, rf):
                self.remove(pp.join(rf+'*'))
                sftp.rmdir(rf)
            else:
                sftp.remove(rf)

    def convertPath(self, p):
        return '/'.join(p.split(os.sep))

    def checkRemotePath(self, sftp, d):
        if d == '':
            return
        if not sgb.lexists(sftp, d):
            self.checkRemotePath(sftp, pp.dirname(d))
            sftp.mkdir(d, mode=0755)

    def checkLocalPath(self, d):
        if d == '':
            return
        if not op.lexists(d):
            self.checkLocalPath(op.dirname(d))
            os.mkdir(d, 0755)

    def putdir(self, ldir, rdir, files=['*']):
        for f in files:
            self.put(op.join(ldir, f), rdir)
        for f in os.listdir(ldir):
            lf = op.join(ldir, f)
            if op.isdir(lf):
                self.putdir(lf, pp.join(rdir, f), files)

    def getdir(self, rdir, ldir, files=['*']):
        for f in files:
            self.get(pp.join(rdir, f), ldir)
        sftp = self.client.open_sftp()
        for f in sftp.listdir(rdir):
            rf = pp.join(rdir, f)
            if sgb.isdir(sftp, rf):
                self.getdir(rf, op.join(ldir, f), files)

if __name__ == '__main__':
    host = '192.168.1.100'
    cli = SshClient()
    cli.connect(host, userid='user')
    cli.command('ls -al')

