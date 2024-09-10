""" Core classes for pyb. 

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

import getopt
import sys
import time
import threading
import traceback

buildFile = 'Not Specified'
debug = False
runtargets = None

class Project:
    """ Class representing a complete project.
    
        The project is executed immediately when it is construction.  You
        can also manually execute it again using the run() method.
    """
    def __init__(self, name='', default=None, targets=None):
        """ Constructor.
        
            @param name: The name of the project
            @param default: The default target to run
            @param targets: Map of targets keyed on the name
        """
        if targets is None:
            targets = {}
        
        self.name = name
        self.default = default
        self.targets = targets
        self.debug = debug
        
        for (name, target) in targets.items():
            target.project = self
            
        self.threads = {}
        
        self.run()
       
    def __call__(self, *args):
        """ Convenience implementation to execute the run() method. """
        self.run()
        
    def run(self):
        """ Execute targets in the project. """
        startTime = time.time()
        try:
            if runtargets is None or len(runtargets) == 0:
                self.targets[self.default].method()
            else:
                for arg in runtargets:
                    try:
                        self.targets[arg].method()
                    except KeyError, e:
                        raise BuildException, 'Unknown target "%s"' % arg
            for t in self.threads.values():
                if debug: print '%s is joining %s' %  (threading.currentThread().getName(), t.getName())
                t.join(10)
        except BuildException, e:
            print '\nBUILD FAILED\n\n%s:%i: %s' % (e.buildfile, e.lineno, 
                e.message)
        except Exception, e:
            print '\nBUILD FAILED\n\n%s' % (e)
            if self.debug:
                print traceback.print_tb(sys.exc_info()[2])
        else:
            print '\nBUILD SUCCESSFUL'
            
        elapsed = time.time() - startTime
        print('Total time: %i seconds' % elapsed)
    
class Target:
    """ Class representing a single build target. """
    def __init__(self, method, depends=None, parallel=False):
        """ Constructor.
        
            @param method: The method to execute which provides this target's
            implementation.
            @param depends: A list of Strings which represent the targets that
            the wrapped target depends upon.
            @param parallel: Set to True to enable parallel execution of the
            task.
        """
        if depends is None:
            depends = []
        self.method = _MethodWrapper(method, self)
        self.depends = depends
        self.parallel = parallel
        
class _MethodWrapper:
    """ Wrap the target body method allowing pre- and post- method code. """
    def __init__(self, method, target):
        """ Constructor.
        
            @param method: The method to wrap
            @param target: The original target object
        """
        self.method = method
        self.target = target
    def __call__(self):
        """ Invoke the wrapped method. """
        # execute dependencies
        for depend in self.target.depends:
            self.target.project.targets[depend].method()
        #execute the wrapped method
        print '\n%s:' % self.method.__name__
        if self.target.parallel:
            if debug: print 'executing %s in parallel' % str(self.method)
            t = threading.Thread(group=None, target=self.method)
            self.target.project.threads[t.getName()] = t
            if debug: print 'starting thread %s' % t.getName()
            t.start()
            if debug: print 'thread running'
        else:
            self.method()
        
class BuildException (Exception):
    """ Raised if an error occurs during the build."""
    def __init__(self, *args):
        """ Constructor.
        
            @param args: must include the message and may also include
            a second argument which is the current task name.
        """
        self.message = args[0]
        if len(args) > 1:
            self.task = args[1]
        self.lineno = sys._getframe(2).f_lineno - 2
        self.buildfile = buildFile
