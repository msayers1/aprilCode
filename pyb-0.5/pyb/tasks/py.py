""" Python related tasks. 

    Copyright (C) 2004  Aetrion LLC

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
"""

import os
import sys

from pyb import core, util
from pyb.core import BuildException


def python(script=None, args=[]):
    """ Execute the specified script using Python.
    
        Note that this task executes Python in a new process.
        
        @param script: The Python script to execute
        @param args: Command-line arguments passed to the script
        @return: A tuple with the stdout and stderr file objects
    """
    taskname = 'python'
    if script is None:
        error = 'Script must be specified'
        util.log(taskname, error)
        raise BuildException(error, taskname)
        
    _script = os.path.normpath(script)
    
    _args = [sys.executable, _script]
    _args.extend(args)
    
    util.log(taskname, "Executing script %s" % _script)
    (child_stdin, child_stdout, child_stderr) = os.popen3(' '.join(_args))
    util.log(taskname, "Script %s completed" % _script)
    return (child_stdout, child_stderr)
    
def epydoc(app=None, format='html', destdir=None, modules=None, url=None, 
top=None, css=None, private=False, privateCss=None, inheritance=None):
    """ Generate documentation using Epydoc.
    
        @param app: The path to epydoc
        @param format: Specify the display format (either 'html' or 'javadoc')
        @param destdir: The destination directory (REQUIRED)
        @param modules: List of modules to document
        @param url: The documented project's URL
        @param top:
        @param css: The CSS stylesheet for the docs
        @param private: Set to True to display private items
        @param inheritance: 
    """
    taskname = 'epydoc'
    
    # try to determine the app location
    if app is None:
        if sys.platform == 'win32':
            app = os.path.join(sys.prefix, 'Scripts', 'epydoc.py')
        else:
            app = os.path.join(sys.prefix, "bin", "epydoc")
    
    if not os.path.exists(app):
        error = 'Cannot find epydoc application %s' % app
        util.log(taskname, error)
        raise BuildException(error, taskname)
    
    if destdir is None:
        error = "Destination directory must be specified"
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    if modules is None:
        error = "You must specify at least one module"
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    
    _destdir = os.path.normpath(destdir)
    
    if not os.path.exists(_destdir):
        os.makedirs(_destdir)
        
    args = [app]
    
    if format == 'html':
        args.append('--html')
    elif format == 'pdf':
        args.append('--pdf')
    
    args.extend(['-o', _destdir])
    
    if url is not None:
        args.extend(['-u', '"%s"' % url])
    if top is not None:
        args.extend(['-t',top])
    if css is not None:
        args.extend(['-c',css])
    if private:
        args.append('--private')
    if privateCss is not None:
        args.extend(['-privatecss', privateCss])
    if inheritance is not None:
        args.append(inheritance)
    
    args.extend(modules)
    
    if core.debug:
        util.log(taskname, 'Current working directory: %s' % os.getcwd())
        
    util.log(taskname, "Generating epydocs into %s" % _destdir)
    if core.debug: util.log(taskname, "Command: %s" % ' '.join(args))
    (child_stdin, child_stdout, child_stderr) = os.popen3(' '.join(args))
    #cmd = app
    #os.spawnv(os.P_WAIT, cmd, args)
    #child_stdin.read()
    #child_stdout.read()
    #child_stderr.read()
    
def setup(file=None, commands=None):
    """ Execute distutils.setup command
    
        @param file: The setup.py file path
        @param commands: A List of commands (sdist, bdist, etc.)
    """
    if file is None:
        error = "You must specify a setup file"
        util.log(taskname, error)
        raise BuildException, (error, task)
        
    _file = os.path.normpath(file)
    
    from distutils.core import run_setup
    run_setup(script_name=_file, script_args=commands)
