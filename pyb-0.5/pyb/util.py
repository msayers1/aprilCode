""" Utility functions. 

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
import re
import sys
import zipfile

from pyb.core import BuildException


INCLUDE = 1
EXCLUDE = 2
    
def filterFiles(basedir, fileFilters=[], filterType=INCLUDE):
    """ Filter files starting from a specified base directory returning a 
        list of files which pass through the filter.
        
        Either basedir or files is required.
        
        @param basedir: The base directory
        @param fileFilters: Compiled regular expressions
        @param filterType: Either INCLUDE or EXCLUDE (defaults to INCLUDE)
        @return: A list of file names
    """
    if basedir is None:
        raise Exception, 'basedir is required'
        
    _basedir = os.path.normpath(basedir)
        
    workingDir = os.getcwd()
    os.chdir(_basedir)
    
    #print "chdir(%s)" % _basedir
    
    fileList = []
    for (root, dirs, files) in os.walk(os.curdir):
        for f in files:
            path = os.path.join(root, f)
            fileList.append(path)
    os.chdir(workingDir)
    return filterFileList(fileList, fileFilters, filterType)
    
        
def filterFileList(files=[], fileFilters=[], filterType=INCLUDE):
    """ Filter a file list.
    
        @param files: The file list
        @param fileFilters:  Compiled regular expressions
        @param filterType: Either INCLUDE or EXCLUDE (defaults to INCLUDE)
        @return: A list of filtered files
    """
    
    #print 'Files to filter: %i' % len(files)
    if len(fileFilters):
        resultFiles = []
        
        if filterType == EXCLUDE:
            resultFiles.extend(files)
        
        for f in files:
            for fileFilter in fileFilters:
                #sys.stdout.write('does %s match %s?' % (f, fileFilter.pattern))
                if fileFilter.search(f):
                    #print 'yes'
                    if filterType == INCLUDE:
                        resultFiles.append(f)
                    elif filterType == EXCLUDE:
                        resultFiles.remove(f)
                    break
        return resultFiles
    else:
        return files
        
def filterNewerFiles(files, regex='', replace=''):
    """ Filter files so that only files which are newer. 
    
        @param files: The source files
        @param regex: ...
        @param replace:  ...
        @return: A filtered list of files
    """
    #print "regex: %s" % regex
    #print "replace: %s" % replace
    filteredFiles = []
    for f in files:
        original = f
        altered = re.sub(regex, replace, f)
        #print "original: %s" % original
        #print "altered: %s" % altered
        if os.path.exists(altered):
            #print "%s exists" % altered
            if os.path.getmtime(original) > os.path.getmtime(altered):
                filteredFiles.append(original)
        else:
            #print "%s does not exist" % altered
            filteredFiles.append(original)
    return filteredFiles
    
def unzip(src, destdir, taskname):
    """ Internal function to unzip the specified file into the given directory.
    
        Build scripts should not call this function directly, rather they
        should use the tasks.core.unzip() function.
    
        src:        The source zip file
        destdir:    The destination directory
        taskname:   The taskname
    """
    if src is None:
        error = 'You must specify a source file'
        log(taskname, error)
        raise BuildException, (error, taskname)
    
    _src = os.path.normpath(src)
    _destdir = os.path.normpath(destdir)
    
    if not os.path.exists(_src):
        error = 'Specified source does not exist'
        log(taskname, error)
        raise BuildException, (error, taskname)
    if not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    log(taskname, 'Extracting files from %s' % _src)
    
    zipFile = zipfile.ZipFile(_src)
    for name in zipFile.namelist():
        path = os.path.join(_destdir, name)
        (head, tail) = os.path.split(path)
        if head and not os.path.exists(head):
            os.makedirs(head)
        destfile = open(path, 'w')
        destfile.write(zipFile.read(name))
        destfile.close()
    zipFile.close()
    
def log(task, message):
    """ Log an error message.
    
        @param task: The task name
        @param message: The message
    """
    print '    [%s] %s' % (task, message)

    

# Unit Tests
import unittest

class _test(unittest.TestCase):
    """ Unit tests for this module """

    def setUp(self):
        basedir = 'test'    
    def testFilterFileList(self):
        files = [
            'test',
            'test/1.java',
            'test/1.foo',
            'test/foo/2.txt',
            'test/bar/foo/'
        ];
        
        #filterMap = {
        #    ['test/1.java','test/1.foo'], [r'.*1']
        #}

        filterStrings = [r'.*1']
        filters = [re.compile(e) for e in filterStrings]
        
        self.assertEquals(files, filterFileList(files))
        self.assertEquals(['test/1.java', 'test/1.foo'], 
            filterFileList(files, filters))
        
        filterFileList(files, filters, INCLUDE)
        filterFileList(files, filters, EXCLUDE)

if __name__ == '__main__':
    unittest.main()
