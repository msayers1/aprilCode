Pyb README
------------------------
Pyb is a build tool written in Python which emulates the style of Ant using Python for build scripts instead of XML.

Installing
------------------------
To install just add the Pyb directory to your PATH environment variable.  This will let you execute Pyb just by typing in 'pyb' on the command line.

Running
------------------------
To run Pyb:

    - Add the Pyb directory to your PATH environment variable
    - Change into the directory with the pybuild.py script
    - Type pyb (or pyb.sh on Unix) on the command line
    
pyb accepts 0 or more target names on the command line.  Targets are executed in the order they appear on the command line.  If no target is specified then the default target which is specified in the build script will be used.

Warning: pyb.sh has not yet been tested.  In fact I have not yet tested pyb on *nix.  If you do find that it is broken please drop me an email, especially if you have a fix. :-)

Questions or comments: me@anthonyeden.com

Last Modified: 4/8/2004
