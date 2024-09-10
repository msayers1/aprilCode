""" Tasks related to Java. 

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
import zipfile

from pyb import core, filters, util
from pyb.core import BuildException


def java(mainclass=None, classpath=None):
    """ Execute the java application.
    
        @param mainclass: The main class to execute (without the .class)
        @param classpath: User-defined classpath
    """
    taskname = 'java'
    if mainclass is None:
        error = 'Main class must be specified'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    
    cmd = __getJavaCommand(taskname)
    args = []
    
    if classpath is not None:
        cp = os.pathsep.join([os.path.normpath(f) for f in classpath])
        args.extend(['-cp', cp])
    
    util.log(taskname, 'Executing %s' % mainclass)
    os.spawnv(os.P_WAIT, cmd, args)
    
def javac(basedir='', destdir='', deprecation=False, debug=True, verbose=False,
optimize=True, classpath=None, target=None, includeFilters=[filters.java],
excludeFilters=[r'.*#.*',filters.cvs], extraArgs=[]):
    """ Execute the javac application.
    
        @param basedir: The base directory (current directory)
        @param destdir: The destination directory (current directory)
        @param deprecation: Set to True to enable deprecation warnings (False)
        @param debug: Set to False to disable debug data in classfiles (True)
        @param optimize: Set to False to disable optimize when compiling (True)
        @param verbose: Set to True for verbose compiler messages (False)
        @param classpath: Specify a custom classpath (None)
        @param target: Specify a target JVM version (None)
        @param includeFilters: Regular expression strings used to include files
                        (All .java files)
        @type includeFilters: list of strings
        @param excludeFilters: Regular expression strings used to exclude files
        @type excludeFilters: list of strings
        @param extraArgs: Extra command-line arguments (empty list)
        @type extraArgs: list of strings
    """
    taskname = 'javac'
    _basedir = os.path.normpath(basedir)
    _destdir = os.path.abspath(os.path.normpath(destdir))
    
    if not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    if not os.path.exists(_destdir):
        os.makedirs(_destdir)

    includeFiltersRe = [re.compile(exp) for exp in includeFilters]
    excludeFiltersRe = [re.compile(exp) for exp in excludeFilters]
    includedFiles = util.filterFiles(_basedir, includeFiltersRe, 
        util.INCLUDE)
    filteredFilesTemp = util.filterFileList(includedFiles, excludeFiltersRe, 
        util.EXCLUDE)
    filteredFiles = util.filterNewerFiles(filteredFilesTemp, r'%s(.*)\.java' % 
        _basedir, r'%s\1.class' % _destdir)
    
    sourceCount = len(filteredFiles)
    if not sourceCount:
        util.log(taskname, "No source files found for compiling")
        return
        
    cmd = __getJavaCommand(taskname)
    
    args = [cmd, '-d', _destdir]
    
    if deprecation:
        args.append('-deprecation')
    if verbose:
        args.append('-verbose')
    if classpath:
        args.extend(['-classpath', os.pathsep.join(
            [os.path.abspath(p) for p in classpath])])
    if target:
        args.extend(['-target', target])
    
    args.extend(extraArgs)
    args.extend(filteredFiles)
                    
    util.log(taskname, 'Compiling %i source files to %s' % (sourceCount, _destdir))
    #util.log(taskname, 'Command: %s' % ' '.join(args))
    
    workingDir = os.getcwd()
    os.chdir(_basedir)
    os.spawnv(os.P_WAIT, cmd, args)
    os.chdir(workingDir)
    
def javadoc(basedir='', destdir='', classpath=None, 
packagenames=[], author=False, version=None, windowtitle=None, doctitle=None, 
header=None, footer=None, bottom=None, overview=None, extraArgs=[],
printstdout=False, printstderror=False):
    """ Execute the javadocs application.
    
        @param basedir: The base directory to find source, i.e. the sourcepath 
            argument in the javadoc tool (current directory)
        @param destdir: The destination directory (current directory)
        @param classpath: Specify a custom classpath (None)
        @type classpath: List of directories and JARs
        @param packagenames: List of package names.  Packages are searched 
        recursively.
        @param author: Set to True to include author in JavaDoc (False)
        @type author: boolean
        @param version: Set to True to include version in JavaDoc (False)
        @param windowtitle: Set the window title string (empty string)
        @param doctitle: Set the document title string (empty string)
        @param header: Path to the header file
        @param footer: Path to the footer file
        @param bottom: Bottom text
        @param overview: Path to the overview file
        @param extraArgs: Extra command-line arguments (empty list)
        @type extraArgs: list of strings
        @param printstdout: Set to True to print all javadoc application output
        @param printstderror: Set to True to print all javadoc stderror output
    """
    taskname = 'javadoc'
    
    if core.debug: util.log(taskname, 'Starting task')

    #print 'checking active count'
    #if core.debug:
    #if True:
        #import threading
        #util.log(taskname, 'Active thread count: %i' % threading.activeCount())
        #print 'active count'
    
    _basedir = os.path.normpath(basedir)
    _destdir = os.path.normpath(destdir)
    
    if overview is not None:
        _overview = os.path.normpath(overview)
    
    if not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    if _destdir and not os.path.exists(_destdir):
        os.makedirs(_destdir)

    cmd = __getJavaCommand(taskname)
    
    args = [cmd, '-quiet', '-d', _destdir]
    
    args.extend(['-sourcepath', _basedir])
    
    if author:
        args.append('-author')
    if overview: 
        args.extend(['-overview', '"%s"' % _overview])
    if header:
        args.extend(['-header', '"%s"' % header])
    if footer:
        args.extend(['-footer', '"%s"' % footer])
    if bottom:
        args.extend(['-bottom', '"%s"' % bottom])
    if doctitle:
        args.extend(['-doctitle', '"%s"' % doctitle])
    if windowtitle:
        args.extend(['-windowtitle', '"%s"' % windowtitle])
        
    args.extend(['"%s"' % s for s in extraArgs])
    #args.extend(filteredFiles)
    args.extend(['-subpackages', ':'.join(packagenames)])
    
    util.log(taskname, 'Generating javadocs to %s' % _destdir)
    if core.debug: util.log(taskname, 'Command: %s' % ' '.join(args))
    #os.spawnv(os.P_WAIT, cmd, args)
    (child_stdin, child_stdout, child_stderr) = os.popen3(' '.join(args))
    if core.debug: util.log(taskname, 'Opened pipe to javadoc application')
    if printstdout:
        print child_stdout
    if printstderror:
        print child_stderr
    if core.debug: util.log(taskname, 'Exiting javadoc task')
    
def jar(basedir='', destfile=None, compress=True, index=False, manifest=None,
includeFilters=[filters.classes], excludeFilters=[], extraArgs=[]):
    """ Execute the jar application.
    
        @param basedir: The base directory (current directory)
        @param destfile: The jar file (REQUIRED)
        @param compress: Set to False to disable compression (True)
        @param index: Set to True to index (False)
        @param manifest: Specify a manifest file
        @param includeFilters: Regular expression strings used to include files
                        (Files ending with .class)
        @param excludeFilters: Regular expression strings used to exclude files
                        (empty list)
        @param extraArgs: Extra command-line arguments (empty list)
    """
    taskname = 'jar'
    if not destfile:
        error = 'You must specify a destination file'
        util.log(taskname, error)
        raise BuildException, ('error', taskname)
    
    _basedir = os.path.normpath(basedir)
    _destfile = os.path.normpath(destfile)
    (_destdir, _destname) = os.path.split(_destfile)
    
    if not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    if _destdir and not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    includeFiltersRe = [re.compile(exp) for exp in includeFilters]
    excludeFiltersRe = [re.compile(exp) for exp in excludeFilters]
    includedFiles = util.filterFiles(_basedir, includeFiltersRe, 
        util.INCLUDE)
    filteredFiles = util.filterFileList(includedFiles, excludeFiltersRe, 
        util.EXCLUDE)
    sourceCount = len(filteredFiles)
    
    cmd = __getJavaCommand(taskname)
    
    flags = ['c', 'f']
    
    args = [cmd]
    
    if not compress:
        flags.append('0')
    if index:
        flags.append('i')
    
    if manifest:
        flags.append('m')
        args.extend([''.join(flags), manifest, _destfile])
    else:
        flags.append('M')
        args.extend([''.join(flags), _destfile])
    
    args.extend(extraArgs)
    
    relativeFilteredFiles = [f.replace(_basedir + os.sep, '') for f in
        filteredFiles]
    
    filesAndCDs = []
    for f in relativeFilteredFiles:
        filesAndCDs.extend(['-C', _basedir, f])

    args.extend(filesAndCDs)
    
    #log(taskname, 'Execution: %s' % ' '.join(args))
    util.log(taskname, 'Generating jar for %i files to %s' %
        (sourceCount, _destfile))
    os.spawnv(os.P_WAIT, cmd, args)
    
def war(basedir='', destfile=None, compress=True, webxml=None, 
includeFilters=[filters.allfiles], excludeFilters=[]):
    """ Create a WAR archive.
    
        @param basedir: The base directory (current directory)
        @param destfile: The ZIP file to write to (REQUIRED)
        @param webxml: The web.xml file (None)
        @param includeFilters: Regular expression strings to include files (All 
        files)
        @param excludeFilters: Regular expression strings to exclude files 
        (empty list)
    """
    taskname = 'war'
    if not destfile:
        error = 'You must specify a destination file'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    
    _basedir = os.path.normpath(basedir)
    _destfile = os.path.normpath(destfile)
    (_destdir, _destname) = os.path.split(_destfile)
    if webxml is not None:
        _webxml = os.path.normpath(webxml)
    
    if not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    if _destdir and not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    workingDir = os.getcwd()
    os.chdir(_basedir)
    
    includeFiltersRe = [re.compile(exp) for exp in includeFilters]
    excludeFiltersRe = [re.compile(exp) for exp in excludeFilters]
    includedFiles = util.filterFiles('', includeFiltersRe, 
        util.INCLUDE)
    filteredFiles = util.filterFileList(includedFiles, excludeFiltersRe, 
        util.EXCLUDE)
    sourceCount = len(filteredFiles)
    
    util.log(taskname, 'Creating war file %s' % _destfile)
    zipFile = zipfile.ZipFile(os.path.join(workingDir, _destfile), 'w')
    for f in filteredFiles:
        zipFile.write(f)
    
    os.chdir(workingDir)
    if webxml is not None:
        zipFile.write(_webxml, '/WEB-INF/web.xml')
    
    zipFile.close()
    
def ear(basedir='', destfile=None, compress=True, appxml=None, 
includeFilters=[filters.allfiles], excludeFilters=[]):
    """ Create an EAR archive.
    
        @param basedir:        The base directory (current directory)
        @param destfile:       The file to write to (REQUIRED)
        @param appxml:         The application.xml file (None)
        @param includeFilters: Regular expression strings to include files
                        (All files)
        @param excludeFilters: Regular expression strings to exclude files
                        (empty list)
    """
    taskname = 'ear'
    if not destfile:
        error = 'You must specify a destination file'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    
    _basedir = os.path.normpath(basedir)
    _destfile = os.path.normpath(destfile)
    (_destdir, _destname) = os.path.split(_destfile)
    
    if not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        util.log(taskname, error)
        raise BuildException, (error, taskname)
    if _destdir and not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    workingDir = os.getcwd()
    os.chdir(_basedir)
    
    includeFiltersRe = [re.compile(exp) for exp in includeFilters]
    excludeFiltersRe = [re.compile(exp) for exp in excludeFilters]
    includedFiles = util.filterFiles('', includeFiltersRe, 
        util.INCLUDE)
    filteredFiles = util.filterFileList(includedFiles, excludeFiltersRe, 
        util.EXCLUDE)
    sourceCount = len(filteredFiles)
    
    util.log(taskname, 'Creating ear file %s' % _destfile)
    zipFile = zipfile.ZipFile(os.path.join(workingDir, _destfile), 'w')
    for f in filteredFiles:
        zipFile.write(f)
    zipFile.close()
    
    os.chdir(workingDir)
    
def unjar(src, destdir):
    """ Unzip the specified jar file into the given directory.
    
        @param src: The source jar file
        @param destdir: The destination directory
    """
    util.unzip(src, destdir, 'unjar')

def unwar(src, destdir):
    """ Unzip the specified war file into the given directory.
    
        @param src: The source war file
        @param destdir: The destination directory
    """
    util.unzip(src, destdir, 'unwar')
    
def __getJavaCommand(commandName):
    """ Construct the full path to a java executable command 
        using the JAVA_HOME environment variable.  If the
        JAVA_HOME environment variable is not set then the application
        prints an error and exits.
        
        @param commandName: The command name        
        @return: The path to a binary
    """
    java_home = os.environ.get("JAVA_HOME")
    if java_home is None:
        print "JAVA_HOME environment variable must be set"
        sys.exit(1)
    cmd = os.path.join(java_home, 'bin', commandName)
    return cmd
