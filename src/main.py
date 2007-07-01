#! /usr/bin/python
# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
main.py is the startup script for NanoEngineer-1.

$Id$

This file should not be imported as the "main" module -- doing so
prints a warning [as of 050902] and doesn't run the contained code.
If necessary, it can be imported as the __main__ module
from within the nE-1 process it starts, by "import __main__".
Such an import doesn't rerun the contained code -- only reload(__main__)
would do that, and that should not be done.

Depending on the details of the package building process,
this file might be renamed and/or moved to a different directory
from the other modules under cad/src. As of 050902, it's always
moved to a different directory (by package building on any platform),
and this is detected at runtime (using __main__.__file__) as a way
of distinguishing end-user runs from developer runs.

When an end-user runs the nE-1 application, OS-dependent code somehow
starts the right python interpreter and has it run this script
(possibly passing command-line arguments, but that might not be implemented yet).

Developers running nE-1 from cvs can run this script using a command line
like "python main.py" or "pythonw main.py", depending on the Python
installation. Some Python or Qt installations require that the absolute
pathname of main.py be used, but the current directory should always be
the one containing this file, when it's run manually in this way.

This script then imports and starts everything else.

As of 041217 everything runs in that one process,
except for occasional temporary subprocesses it might start.

History:

[mostly unrecorded except in cvs; originally by Josh; lots of changes by
various developers.]

bruce 050902 revised module docstring, and added comments explaining why
there are two separate tests of __name__ == '__main__'
(which surrounds most code in this module).
The reason this condition is needed at all is to reduce the harm caused
by someone accidentally running "import main" (which is wrong but causes no harm).
"""

__author__ = "Josh"

import sys, os, time

print
print "starting NanoEngineer-1 in [%s]," % os.getcwd(), time.asctime() #bruce 070429

#bruce 061222: define global flags (available to other modules via import __main__) that indicate
# whether we're in the Qt3 or Qt4 version of NE1. This works by hardcoding the flags differently
# in the MAIN and wware_qt4_20060919 cvs branches. Here, we set them for Qt4:
USING_Qt3 = False
USING_Qt4 = True

if __name__ != '__main__':
    #bruce 050902 added this warning
    print
    print "Warning: main.py should not be imported except as the __main__ module."
    print " (It is now being imported under the name %r.\n" \
          "  This is a bug, but should cause no direct harm.)" % (__name__,)
    print

import startup_funcs # this has no side effects, it only defines a few functions
    # bruce 050902 moved some code from this file into new module startup_funcs

# all other imports should be added lower down

if __name__ == '__main__':
    # This condition surrounds most code in this file, but it occurs twice,
    # so that the first occurrence can come before most of the imports,
    # while letting most imports occur at the top level of the file.
    # [bruce 050902 comment about older situation]
    
    main_globals = globals() # needed in case .atom-debug-rc is executed, since it must be executed in that global namespace
    
    startup_funcs.before_most_imports( main_globals )
        # "Do things that should be done before anything that might possibly have side effects."

# most imports in this file should be done here, or inside functions in startup_funcs



from PyQt4.Qt import QApplication, QSplashScreen ## bruce 050902 removed QRect, QDesktopWidget

## from constants import *
    #bruce 050902 removing import of constants since I doubt it's still needed here.
    # This might conceivably cause bugs, but it's unlikely.

if __name__ == '__main__':
    # [see comment above about why there are two occurrences of this statement]
    
    startup_funcs.before_creating_app()
        # "Do whatever needs to be done before creating the application object, but after importing MWsemantics."
    
    QApplication.setColorSpec(QApplication.CustomColor)
    app = QApplication(sys.argv)
    
    # If the splash image is found in cad/images, put up a splashscreen. 
    # If you don't want the splashscreen, just rename the splash image.
    # mark 060131.
    from Utility import imagename_to_pixmap
    splash_pixmap = imagename_to_pixmap( "images/splash.png" ) # rename it if you don't want it.
    if not splash_pixmap.isNull():
        splash = QSplashScreen(splash_pixmap) # create the splashscreen
        splash.show()
        MINIMUM_SPLASH_TIME = 3.0 
            # I intend to add a user pref for MINIMUM_SPLASH_TIME for A7. mark 060131.
        splash_start = time.time()
    else:
        print "note: splash.png was not found"
 
    from PyQt4.Qt import SIGNAL
    app.connect(app, SIGNAL("lastWindowClosed ()"), app.quit)

    from MWsemantics import MWsemantics # (this might have side effects other than defining things)

    from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
    ##########################################################################################################
    #
    # The debug preference menu is now working in Qt 4 but you can't effectively change this debug
    # preference after the program has already come up, as too much of the GUI is already in place
    # by then. To change it, manually edit it here.
    #
    debug_pref("Multipane GUI", Choice_boolean_True)
    #debug_pref("Multipane GUI", Choice_boolean_False)
    #
    ##########################################################################################################

    # These should move to a generic initialization function when there
    # are more of them.  Are they in the right place?  Probably should be
    # called before any assembly objects are created.
    import assembly
    assembly.assembly.initialize()
    import GroupButtonMixin
    GroupButtonMixin.GroupButtonMixin.initialize()
    
    foo = MWsemantics() # This does a lot of initialization (in MainWindow.__init__)

    import CoNTubGenerator
    CoNTubGenerator.initialize()

    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_pre_main_show
    except:
        pass
    else:
        meth()

    startup_funcs.pre_main_show(foo) # this sets foo's geometry, among other things
    
    foo._init_after_geometry_is_set()
    
    if not splash_pixmap.isNull():
        # If the MINIMUM_SPLASH_TIME duration has not expired, sleep for a moment.
        while time.time() - splash_start < MINIMUM_SPLASH_TIME:
            time.sleep(0.1)
        splash.finish( foo ) # Take away the splashscreen
    
    foo.show() # show the main window

    if sys.platform != 'darwin': #bruce 070515 add condition to disable this on Mac, until Brian fixes the hang on Mac
        from Sponsors import PermissionDialog
##        print "start sponsors startup code"
        # Show the dialog that asks permission to download the sponsor logos, then
        # launch it as a thread to download and process the logos.
        #
        permdialog = PermissionDialog(foo)
        if permdialog.needToAsk:
            permdialog.exec_()
        permdialog.start()
##        print "end sponsors startup code"
        
    if not debug_pref("Multipane GUI", Choice_boolean_False):
        if foo.glpane.mode.modename == 'DEPOSIT':
            # Two problems are addressed here when nE-1 starts in Build (DEPOSIT) mode.
            # 1. The MMKit can cover the splashscreen (bug #1439).
            #   BTW, the other part of bug fix 1439 is in MWsemantics.modifyMMKit()
            # 2. The MMKit appears 1-3 seconds before the main window.
            # Both situations now resolved.  mark 060202
            # Should this be moved to startup_funcs.post_main_show()? I chose to leave
            # it here since the splashscreen code it refers to is in this file.  mark 060202.
            foo.glpane.mode.MMKit.show()        
    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_post_main_show 
    except:
        pass
    else:
        meth()

    startup_funcs.post_main_show(foo) # bruce 050902 added this

    # If the user's .atom-debug-rc specifies PROFILE_WITH_HOTSHOT=True, use hotshot, otherwise
    # fall back to vanilla Python profiler.
    try:
        PROFILE_WITH_HOTSHOT
    except NameError:
        PROFILE_WITH_HOTSHOT = False
    
    # now run the main Qt event loop --
    # perhaps with profiling, if user requested this via .atom-debug-rc.
    try:
        # user can set this to a filename in .atom-debug-rc,
        # to enable profiling into that file
        atom_debug_profile_filename 
        if atom_debug_profile_filename:
            print "user's .atom-debug-rc requests profiling into file %r" % (atom_debug_profile_filename,)
            if not type(atom_debug_profile_filename) in [type("x"), type(u"x")]:
                print "error: atom_debug_profile_filename must be a string; running without profiling"
                assert 0 # caught and ignored, turns off profiling
            if PROFILE_WITH_HOTSHOT:
                try:
                    import hotshot
                except:
                    print "error during 'import hotshot'; running without profiling"
                    raise # caught and ignored, turns off profiling
            else:
                try:
                    import profile
                except:
                    print "error during 'import profile'; running without profiling"
                    raise # caught and ignored, turns off profiling
    except:
        atom_debug_profile_filename = None

    # bruce 041029: create fake exception, to help with debugging
    # (in case it's shown inappropriately in a later traceback)
    try:
        assert 0, "if you see this exception in a traceback, it is from" \
            " the startup script main.py, not the code that printed the traceback"
    except:
        pass

    from platform import atom_debug
    if atom_debug:
        # Use a ridiculously specific keyword, so this isn't triggered accidentally.
        if len(sys.argv) >= 3 and sys.argv[1] == '--initial-file':
            # fileOpen gracefully handles the case where the file doesn't exist.
            foo.fileOpen(sys.argv[2])
            if len(sys.argv) > 3:
                import env
                from HistoryWidget import orangemsg
                env.history.message(orangemsg("We can only import one file at a time."))
  
    if atom_debug_profile_filename:
        if PROFILE_WITH_HOTSHOT:
            profile = hotshot.Profile(atom_debug_profile_filename)
            profile.run('app.exec_()')
        else:
            profile.run('app.exec_()', atom_debug_profile_filename)
        print "\nprofile data was presumably saved into %r" % (atom_debug_profile_filename,)
    else:
        # if you change this code, also change the string literal just above
        app.exec_() 

    pass

# end
