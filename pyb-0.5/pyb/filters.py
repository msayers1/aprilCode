""" Module which contains a bunch of useful regular expression filters. 

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


allfiles = r'.*'
cvs = r'.*CVS%s.*' % os.sep
hidden = r'.*%s\..*' % os.sep
java = r'.*\.java'
classes = r'.*\.class'
jars = r'.*\.jar'
py = r'.*\.py$'
pyc = r'.*\.pyc'
