python_ssh_client
=================

Wrapper classes to execute commands remotely or to transfer files via SSH
using paramiko module

- SshClient.py
  remote command execution, file put/get via sftp.
  if there is no path on remote server, this class makes the path then write the file.

- SshGlob.py
  it's similar to the Lib/Glob.py but it additionally support the remote file glob
  as well as exist check

This source code is distributed under BSD License.
The use of this code implies you agree the license.

Copyright (c) 2013, Jinserk Baik All rights reserved.
