""" Tasks related to Jython. 

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
from pyb import util
from pyb.core import BuildException


def jythonc(basedir='', modules=[], package=None, jarfile=None, workingdir=None, 
deep=False, core=False, all=False, addpackages=[], jythonc=None, compiler=None, 
compileropts=None):
    """ Compile python classes into Java class files.
    
        @param basedir: The base directory
        @param modules: List of python modules (either .py or modules in path)
        @param package: The package name to use
        @param jarfile: The JAR file to output to
        @param workingdir: Directory where java source code is placed
        @param deep: Compile python dependencies (for applets)
        @param core: Include core Python libraries (130k)
        @param all: Everything in core plus the compiler and parser
        @param addpackages: Include Java dependencies from the given packages
        @param compiler: The path to the compiler to use
        @param compileropts: Options to pass to the compiler
    """
    taskname = 'jythonc'
    
    if jythonc is None:
        error = 'You must specify the location of the jythonc compiler'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    
    _basedir = os.path.normpath(basedir)
    _jythonc = os.path.normpath(jythonc)
    
    if workingdir is not None:
        _workingdir = os.path.normpath(workingdir)
    if compiler is not None:
        _compiler = os.path.normpath(compiler)
    
    if not os.path.exists(jythonc):
        error = 'The jythonc application %s does not exist' % _jythonc
        util.log(taskname, error)
        raise BuildException, (taskname, error)
    
    cmd = _jythonc
    args = [cmd]
    
    if package is not None:
        args.extend(["-p", package])
    if jarfile is not None:
        args.extend(["-j", jarfile])
    if workingdir is not None:
        args.extend(['-w', _workingdir])
    if deep:
        args.append("-d")
    if core:
        args.append("-c")
    if all:
        args.append("-a")
    if len(addpackages) > 0:
        args.extend(["-A", ','.join(addpackages)])
    if compiler is not None:
        args.extend(['-C', _compiler])
    if compileropts is not None:
        args.extend(['-J', compileropts])
        
    args.extend(modules)
    
    workingDir = os.getcwd()
    os.chdir(_basedir)
    util.log(taskname, 'Compiling with jythonc')
    os.spawnv(os.P_WAIT, cmd, args)
    os.chdir(workingDir)
