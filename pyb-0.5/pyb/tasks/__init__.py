""" Task module which contains all the core tasks for Pyb. 

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

import inspect
import os
import re
import shutil
import sys

import bz2
import gzip as gzipfile
import tarfile
import zipfile

from pyb import filters
from pyb import core
from pyb import util
from pyb.core import BuildException


def copy(src=None, basedir=None, destdir='', includeFilters=[filters.allfiles], excludeFilters=[filters.cvs], debug=False):
    """ Copy files and directories from one location to another.
        
        Either the src or the basedir parameters must be specified.
        
        @param src: The source file
        @param basedir: The base directory
        @param destdir: The destination directory (current directory)
        @param includeFilters: Regular expression strings used to include files
                        (All Files)
        @param excludeFilters: Regular expression strings used to exclude files
        @param debug: Set to True to enable debugging
    """
    taskname = 'copy'
    
    if src is None and basedir is None:
        error = "Either the source or basedir must be specified"
        log(taskname, error)
        raise BuildException, (error, taskname)
    
    if src is not None:
        _src = os.path.normpath(src)
    if basedir is not None:
        _basedir = os.path.normpath(basedir)
    _destdir = os.path.abspath(os.path.normpath(destdir))
    
    if src is not None and not os.path.exists(_src):
        error = 'Specified source file does not exist'
        log(taskname, error)
        raise BuildException, (error, taskname)
    if basedir is not None and not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        log(taskname, error)
        raise BuildException, (error, taskname)
    if not os.path.exists(_destdir):
        os.makedirs(_destdir)
   
    if src is not None:
        shutil.copy(src, _destdir)
    else:
        includeFiltersRe = [re.compile(exp) for exp in includeFilters]
        excludeFiltersRe = [re.compile(exp) for exp in excludeFilters]
        includedFiles = util.filterFiles(_basedir, includeFiltersRe,
            util.INCLUDE)
        
        
        filteredFiles = util.filterFileList(includedFiles, excludeFiltersRe, 
            util.EXCLUDE)
        
        #filteredFiles = util.filterNewerFiles(filteredFilesTemp, r'%s(.*)' % _basedir, r'%s\1' % _destdir)
        
        sourceCount = len(filteredFiles)
        
        log(taskname, 'Copying %i files from %s to %s' %
            (sourceCount, _basedir, _destdir))
        for f in filteredFiles:
            fin = os.path.join(_basedir, f)
            fout = os.path.join(_destdir, f)
            #if debug: print 'copy src: %s' % fin
            #if debug: print 'copy dest: %s' % fout
            (head, tail) = os.path.split(fout)
            if not os.path.exists(head):
                os.makedirs(head)
            shutil.copyfile(fin, fout)
    
def sleep(s):
    """ Sleep for s seconds.
    
        @param s Number of seconds to sleep
    """
    print 'sleeping'
    taskname = 'sleep'
    import time
    util.log(taskname, 'Sleeping for %d seconds' % s)
    for i in range(1, s):
        time.sleep(1)
        print i
    
def tar(basedir='', destfile=None, compression='none',
includeFilters=[filters.allfiles], excludeFilters=[]):
    """ Create a tar archive.
    
        basedir:        The base directory (current directory)
        destfile:       The tar file to write to (REQUIRED)
        compression:    'none', 'gzip' or 'bzip2' ('none')
        includeFilters: Regular expression Strings to include files
        (All files)
        excludeFilters: Regular expression strings to exclude files
        (empty list)
    """
    
    if not destfile:
        error = 'You must specify a destination file'
        log('tar', error)
        raise BuildException, (error, 'tar')
    
    _basedir = os.path.normpath(basedir)
    _destfile = os.path.normpath(destfile)
    (_destdir, _destname) = os.path.split(_destfile)
    
    if not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        log('tar', error)
        raise BuildException, (error, 'tar')
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
    
    if compression == 'gzip':
        mode = 'w:gz'
    elif compression == 'bzip2':
        mode = 'w:bz2'
    else:
        mode = 'w:'
    
    log('tar', 'Creating tar file %s with compression %s' % 
        (_destfile, compression))
    tarFile = tarfile.open(os.path.join(workingDir, _destfile), mode)
    for f in filteredFiles:
        tarFile.add(f, None, False)
    tarFile.close()
    
    os.chdir(workingDir)
    
def untar(src=None, destdir=''):
    """ Untar the specified file.
    
        src:        The source tar file
        destdir:    The destination directory (current directory)
    """
    taskname = 'untar'
    
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
    
    tarFile = tarfile.open(_src)
    workingDir = os.getcwd()
    os.chdir(_destdir)
    for tarInfo in tarFile:
        tarFile.extract(tarInfo)
    tarFile.close()
    
    os.chdir(workingDir)
    
def gzip(src=None, destfile=None):
    """ Compress a file using gzip.
    
        src:            The source file to gzip (REQUIRED)
        destfile:       The gzip file to write to (REQUIRED)
    """
    
    if not src:
        error = 'You must specify a source file'
        log('gzip', error)
        raise BuildException, (error, 'gzip')
    if not destfile:
        error = 'You must specify a destination file'
        log('gzip', error)
        raise BuildException, (error, 'gzip')
    
    _src = os.path.normpath(src)
    _destfile = os.path.normpath(destfile)
    (_destdir, _destname) = os.path.split(_destfile)
    
    if not os.path.exists(_src):
        error = 'Specified source file does not exist'
        log('gzip', error)
        raise BuildException, (error, 'gzip')
    if _destdir and not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    log('gzip', 'Creating gzip file %s from %s' % (_destfile, _src))
    gzipFile = gzipfile.open(_destfile, 'wb')
    srcFile = open(_src, 'rb')
    gzipFile.write(srcFile.read())
    gzipFile.close()
    srcFile.close()

def gunzip(src, destfile=None, destdir=None):
    """ Decompress a gzip file.
        
        Either destfile or destdir must be specified.
    
        src:        The source gzip file (REQUIRED)
        destfile:   The file to write to
        destdir:    The directory to write to
    """
    
    if not src:
        error = 'You must specify a source file'
        log('gunzip', error)
        raise BuildException, (error, 'gunzip')
    if not destfile and not destdir:
        error = 'You must specify a destination file or directory'
        log('gunzip', error)
        raise BuildException, (error, 'gunzip')
    
    _src = os.path.normpath(src)
    
    if destfile is not None:
        _destfile = os.path.normpath(destfile)
        _realdest = _destfile
        (_destdir, _destname) = os.path.split(_destfile)
    else:
        _destdir = os.path.normpath(destdir)
        (srchead, srctail) = os.path.split(_src)
        _parts = srctail.split('.')
        _newname ='.'.join(_parts[0:(len(_parts) - 1)])
        _realdest = os.path.join(_destdir, _newname)
    
    if not os.path.exists(_src):
        error = 'Specified source file does not exist'
        log('gunzip', error)
        raise BuildError, (error, 'gunzip')
    if not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    log('gunzip', 'Decompressing gzip file %s to %s' % (_src, _realdest))
    gzipFile = gzipfile.open(_src)
    destFile = open(_realdest, 'w')
    destFile.write(gzipFile.read())
    gzipFile.close()
    destFile.close()
    
def bzip2(src='', destfile=None, includeFilters=[filters.allfiles],
excludeFilters=[]):
    """ Compress a file using bzip2.
    
        src:            The source file to gzip (REQUIRED)
        destfile:       The gzip file to write to (REQUIRED)
    """
    taskname = 'bzip2'
    if not src:
        error = 'You must specify a source file'
        log(taskname, error)
        raise BuildException, (error, taskname)
    if not destfile:
        error = 'You must specify a destination file'
        log(taskname, error)
        raise BuildException, (error, taskname)
    
    _src = os.path.normpath(src)
    _destfile = os.path.normpath(destfile)
    (_destdir, _destname) = os.path.split(_destfile)
    
    if not os.path.exists(_src):
        error = 'Specified source file does not exist'
        log(taskname, error)
        raise BuildException, (error, taskname)
    if _destdir and not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    log(taskname, 'Creating bzip2 file %s from %s' % (_destfile, _src))
    bz2File = bz2.BZ2File(_destfile, 'wb')
    srcFile = open(_src, 'rb')
    bz2File.write(srcFile.read())
    bz2File.close()
    srcFile.close()
    
def bunzip2(src, destfile=None, destdir=None):
    """ Decompress a bzip2 file.
        
        Either destfile or destdir must be specified.
    
        src:        The source gzip file (REQUIRED)
        destfile:   The file to write to
        destdir:    The directory to write to
    """
    taskname = 'bunzip2'
    if not src:
        error = 'You must specify a source file'
        log(taskname, error)
        raise BuildException, (error, taskname)
    if not destfile and not destdir:
        error = 'You must specify a destination file or directory'
        log(taskname, error)
        raise BuildException, (error, taskname)
    
    _src = os.path.normpath(src)
    
    if destfile is not None:
        _destfile = os.path.normpath(destfile)
        _realdest = _destfile
        (_destdir, _destname) = os.path.split(_destfile)
    else:
        _destdir = os.path.normpath(destdir)
        (srchead, srctail) = os.path.split(_src)
        _parts = srctail.split('.')
        _newname ='.'.join(_parts[0:(len(_parts) - 1)])
        _realdest = os.path.join(_destdir, _newname)
    
    if not os.path.exists(_src):
        error = 'Specified source file does not exist'
        log(taskname, error)
        raise BuildError, (error, taskname)
    if _destdir and not os.path.exists(_destdir):
        os.makedirs(_destdir)
    
    log(taskname, 'Decompressing bzip2 file %s to %s' % (_src, _realdest))
    bzipFile = bz2.BZ2File(_src)
    destFile = open(_realdest, 'w')
    destFile.write(bzipFile.read())
    bzipFile.close()
    destFile.close()
    
def zip(basedir='', destfile=None, compress=True,
includeFilters=[filters.allfiles], excludeFilters=[]):
    """ Create a zip archive.
    
        basedir:        The base directory (current directory)
        destfile:       The ZIP file to write to (REQUIRED)
        compress:       Set to false to disable compression (True)
        includeFilters: Regular expression Strings to include files
        (All files)
        excludeFilters: Regular expression strings to exclude files
        (empty list)
    """
    
    if not destfile:
        error = 'You must specify a destination file'
        log('zip', error)
        raise BuildException, (error, 'zip')
    
    _basedir = os.path.normpath(basedir)
    _destfile = os.path.normpath(destfile)
    (_destdir, _destname) = os.path.split(_destfile)
    #print '_destdir: %s' % _destdir
    
    if _basedir and not os.path.exists(_basedir):
        error = 'Specified base directory does not exist'
        log('zip', error)
        raise BuildException, (error, 'zip')
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
    
    if compress:
        compression = zipfile.ZIP_DEFLATED
    else:
        compression = zipfile.ZIP_STORE
    
    log('zip', 'Creating zip file %s' % _destfile)
    zipFile = zipfile.ZipFile(os.path.join(workingDir, _destfile), 'w', 
        compression)
    for f in filteredFiles:
        zipFile.write(f)
    zipFile.close()
    
    os.chdir(workingDir)
    
def unzip(src, destdir):
    """ Unzip the specified file into the given directory.
    
        src:        The source zip file
        destdir:    The destination directory
        taskname:   The taskname
    """
    util.unzip(src, destdir, 'unzip')
    
def fail(message=None, task=None):
    """ Force the build to fail.
    
        message:    The reason for the failure
        task:       The name of the task
    """
    raise BuildException, (message, task)
    
def delete(file=None, dir=None):
    """ Delete the specified file or directory.
    
        Either the file or the dir must be specified.
    
        file:   The file path
        dir:    The directory path
    """
    taskname = __name__
    if file is None and dir is None:
        error = 'You must specify either a file or a directory'
        log('delete', error)
        raise BuildException, (error, 'delete')
        
    if file:
        _file = os.path.normpath(file)
        if os.path.exists(_file):
            log('delete', 'Deleting file %s' % _file)
            os.remove(_file)
        else:
            error = 'Warning: File %s does not exist' % _file
            log('delete', error)
            #raise BuildException, (error, 'delete')
    if dir:
        _dir = os.path.normpath(dir)
        if os.path.exists(_dir):
            log('delete', 'Deleting directory %s' % _dir)
            shutil.rmtree(dir)
        else:
            error = 'Warning: Directory %s does not exist' % _dir
            log('delete', error)
            #raise BuildException, (error, 'delete')

def log(taskname, message):
    util.log(taskname, message)

