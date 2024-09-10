#!/usr/bin/env python

""" Bootstrap script which invokes the build.py script in the current directory.

    You can use this bootstrap by putting the directory containing it in your
    PATH environment variable.  On Windows machines you can then use 'pyb' to 
    execute, or you can use pyb.py on *nix machines.
    
    -d Enable debugging
    -f Specify the build file
    
    Copyright (C) 2004  Aetrion LLC

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    @author: Anthony Eden
    @copyright: Aetrion LLC, All Rights Reserved
"""

import getopt
import os
import sys
import threading

from pyb import util
from pyb import core

class Worker(threading.Thread):
    def run(self):
        buildFile = None
        
        opts, args = getopt.getopt(sys.argv[1:], 'df:')
        for o, a in opts:
            if o == '-d':
                print 'Debugging enabled'
                core.debug = True
            if o == '-f':
                buildFile = a
        core.runtargets = args
        
        if buildFile is None:
            buildFile = 'pybuild.py'
        core.buildFile = buildFile
        
        cwd = os.getcwd()
        
        buildFileAbs = os.path.abspath(buildFile)
        if os.path.exists(buildFileAbs):
            print 'Buildfile: %s' % buildFile
        else:
            print 'Buildfile: %s not found!' % buildFile
            print 'Build failed.'
            sys.exit(1)
        
        buildPath, buildFileName = os.path.split(buildFileAbs)
        buildName, buildExt = os.path.splitext(buildFileName)
        sys.path.insert(0, buildPath)
        
        # The import here automatically runs the code in the body
        # of pybuild
        __import__(buildName)

if __name__ == '__main__':
    Worker().start()
