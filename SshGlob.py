#!/usr/bin/python
###########################################################################
#
#   SshGlob.py
#       filename globbing utility for SSH remote host
#       imported from the Lib/glob.py
#
#   Jinserk Baik <jinserk.baik@gmail.com>
#   
#   This source code is distributed under BSD License.
#   The use of this code implies you agree the license.
#
#   Copyright (c) 2013, Jinserk Baik All rights reserved.
#
###########################################################################

import sys, os, re, stat
import posixpath as pp
import fnmatch

try:
    _unicode = unicode
except NameError:
    # If Python is built without Unicode support, the unicode type
    # will not exist. Fake one.
    class _unicode(object):
        pass

def isdir(sftp, pathname):
    if stat.S_ISDIR(sftp.stat(pathname).st_mode):
        return True
    else:
        return False

def exists(sftp, pathname):
    try:
        filestat = sftp.stat(pathname)
        return True
    except IOError:
        return False

def lexists(sftp, pathname):
    try:
        filestat = sftp.lstat(pathname)
        return True
    except IOError:
        return False

def glob(sftp, pathname):
    """Return a list of paths matching a pathname pattern.
    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns."""
    return list(iglob(sftp, pathname))


def iglob(sftp, pathname):
    """Return an iterator which yields the paths matching a pathname pattern.
    The pattern may contain simple shell-style wildcards a la
    fnmatch. However, unlike fnmatch, filenames starting with a
    dot are special cases that are not matched by '*' and '?'
    patterns."""
    if not has_magic(pathname):
        if lexists(sftp, pathname):
            yield pathname
        return
    dirname, basename = pp.split(pathname)
    if not dirname:
        for name in glob1(sftp, sftp.getcwd(), basename):
            yield name
        return
    # `pp.split()` returns the argument itself as a dirname if it is a
    # drive or UNC path.  Prevent an infinite recursion if a drive or UNC path
    # contains magic characters (i.e. r'\\?\C:').
    if dirname != pathname and has_magic(dirname):
        dirs = iglob(dirname)
    else:
        dirs = [dirname]
    if has_magic(basename):
        glob_in_dir = glob1
    else:
        glob_in_dir = glob0
    for dirname in dirs:
        for name in glob_in_dir(sftp, dirname, basename):
            yield pp.join(dirname, name)

# These 2 helper functions non-recursively glob inside a literal directory.
# They return a list of basenames. `glob1` accepts a pattern while `glob0`
# takes a literal basename (so it only has to check for its existence).

def glob1(sftp, dirname, pattern):
    if not dirname:
        dirname = sftp.getcwd()
    if isinstance(pattern, _unicode) and not isinstance(dirname, unicode):
        dirname = unicode(dirname, sys.getfilesystemencoding() or
                                   sys.getdefaultencoding())
    try:
        names = sftp.listdir(dirname)
    except IOError:
        return []
    if pattern[0] != '.':
        names = filter(lambda x: x[0] != '.', names)
    return fnmatch.filter(names, pattern)

def glob0(sftp, dirname, basename):
    if basename == '':
        # `pp.split()` returns an empty basename for paths ending with a
        # directory separator.  'q*x/' should match only directories.
        if isDir(sftp, dirname):
            return [basename]
    else:
        if sftp.lexists(pp.join(dirname, basename)):
            return [basename]
    return []

magic_check = re.compile('[*?[]')

def has_magic(s):
    return magic_check.search(s) is not None

