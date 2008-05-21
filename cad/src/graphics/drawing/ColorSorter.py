# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ColorSorter.py - A class to group primitive drawing by colors.

This was originally done as a GL optimization to minimize calls on
apply_material.

Later, it was extended to handle multiple display lists per Chunk object as an
optimization to avoid rebuilding a single display list when the appearance of
the object changes for hover-highlighting and selection.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

Originated by Josh as drawer.py .

Various developers extended it since then.

Brad G. added ColorSorter features.

At some point Bruce partly cleaned up the use of display lists.

071030 bruce split some functions and globals into draw_grid_lines.py
and removed some obsolete functions.

080210 russ Split the single display-list into two second-level lists (with and
without color) and a set of per-color sublists so selection and hover-highlight
can over-ride Chunk base colors.  ColorSortedDisplayList is now a class in the
parent's displist attr to keep track of all that stuff.

080311 piotr Added a "drawpolycone_multicolor" function for drawing polycone
tubes with per-vertex colors (necessary for DNA display style)

080313 russ Added triangle-strip icosa-sphere constructor, "getSphereTriStrips".

080420 piotr Solved highlighting and selection problems for multi-colored
objects (e.g. rainbow colored DNA structures).

080519 russ pulled the globals into a drawing_globals module and broke drawer.py
into 10 smaller chunks: glprefs.py setup_draw.py shape_vertices.py
ColorSorter.py CS_workers.py CS_ShapeList.py CS_draw_primitives.py drawers.py
gl_lighting.py gl_buffers.py
"""

import os
import sys

# the imports from math vs. Numeric are as discovered in existing code
# as of 2007/06/25.  It's not clear why acos is coming from math...
from math import floor, ceil, acos, atan2
import Numeric
from Numeric import sin, cos, sqrt, pi
degreesPerRadian = 180.0 / pi

# russ 080519 No doubt many of the following imports are unused.
# When the dust settles, the unnecessary ones will be removed.
from OpenGL.GL import GL_AMBIENT
from OpenGL.GL import GL_AMBIENT_AND_DIFFUSE
from OpenGL.GL import glAreTexturesResident
from OpenGL.GL import GL_ARRAY_BUFFER_ARB
from OpenGL.GL import GL_BACK
from OpenGL.GL import glBegin
from OpenGL.GL import glBindTexture
from OpenGL.GL import GL_BLEND
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glCallList
from OpenGL.GL import glColor3f
from OpenGL.GL import glColor3fv
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_COLOR_MATERIAL
from OpenGL.GL import GL_COMPILE
from OpenGL.GL import GL_COMPILE_AND_EXECUTE
from OpenGL.GL import GL_CONSTANT_ATTENUATION
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_CURRENT_BIT
from OpenGL.GL import glDeleteLists
from OpenGL.GL import glDeleteTextures
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import GL_DIFFUSE
from OpenGL.GL import glDisable
from OpenGL.GL import glDisableClientState
from OpenGL.GL import glDrawArrays
from OpenGL.GL import glDrawElements
from OpenGL.GL import glDrawElementsub
from OpenGL.GL import glDrawElementsui
from OpenGL.GL import glDrawElementsus
from OpenGL.GL import GL_ELEMENT_ARRAY_BUFFER_ARB
from OpenGL.GL import glEnable
from OpenGL.GL import glEnableClientState
from OpenGL.GL import glEnd
from OpenGL.GL import glEndList
from OpenGL.GL import GL_EXTENSIONS
from OpenGL.GL import GL_FALSE
from OpenGL.GL import GL_FILL
from OpenGL.GL import glFinish
from OpenGL.GL import GL_FLOAT
from OpenGL.GL import GL_FOG
from OpenGL.GL import GL_FOG_COLOR
from OpenGL.GL import GL_FOG_END
from OpenGL.GL import GL_FOG_MODE
from OpenGL.GL import GL_FOG_START
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import glGenLists
from OpenGL.GL import glGenTextures
from OpenGL.GL import glGetString
from OpenGL.GL import GL_LIGHT0
from OpenGL.GL import GL_LIGHT1
from OpenGL.GL import GL_LIGHT2
from OpenGL.GL import glLightf
from OpenGL.GL import glLightfv
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_LINE
from OpenGL.GL import GL_LINEAR
from OpenGL.GL import GL_LINE_LOOP
from OpenGL.GL import GL_LINES
from OpenGL.GL import GL_LINE_SMOOTH
from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glLineWidth
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import glMaterialf
from OpenGL.GL import glMaterialfv
from OpenGL.GL import glMatrixMode
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glNewList
from OpenGL.GL import glNormal3fv
from OpenGL.GL import glNormalPointer
from OpenGL.GL import glNormalPointerf
from OpenGL.GL import GL_NORMAL_ARRAY
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import glPointSize
from OpenGL.GL import GL_POINTS
from OpenGL.GL import GL_POINT_SMOOTH
from OpenGL.GL import GL_POLYGON
from OpenGL.GL import glPolygonMode
from OpenGL.GL import glPopAttrib
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glPopName
from OpenGL.GL import GL_POSITION
from OpenGL.GL import glPushAttrib
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPushName
from OpenGL.GL import GL_QUADS
from OpenGL.GL import GL_QUAD_STRIP
from OpenGL.GL import GL_RENDERER
from OpenGL.GL import GL_RGBA
from OpenGL.GL import glRotate
from OpenGL.GL import glRotatef
from OpenGL.GL import GL_SHININESS
from OpenGL.GL import GL_SPECULAR
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import GL_STATIC_DRAW
from OpenGL.GL import glTexCoord2f
from OpenGL.GL import glTexCoord2fv
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glTranslate
from OpenGL.GL import glTranslatef
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_TRIANGLE_STRIP
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_UNSIGNED_BYTE
from OpenGL.GL import GL_UNSIGNED_SHORT
from OpenGL.GL import GL_VENDOR
from OpenGL.GL import GL_VERSION
from OpenGL.GL import glVertex
from OpenGL.GL import glVertex2f
from OpenGL.GL import glVertex3f
from OpenGL.GL import glVertex3fv
from OpenGL.GL import GL_VERTEX_ARRAY
from OpenGL.GL import glVertexPointer
from OpenGL.GL import glVertexPointerf

from OpenGL.GLU import gluBuild2DMipmaps

from geometry.VQT import norm, vlen, V, Q, A

from utilities.constants import white, blue, red
from utilities.constants import darkgreen, lightblue
from utilities.constants import DIAMOND_BOND_LENGTH
from utilities.prefs_constants import material_specular_highlights_prefs_key
from utilities.prefs_constants import material_specular_shininess_prefs_key
from utilities.prefs_constants import material_specular_finish_prefs_key
from utilities.prefs_constants import material_specular_brightness_prefs_key

from utilities.debug_prefs import Choice
import utilities.debug as debug # for debug.print_compact_traceback

#=

import graphics.drawing.drawing_globals as drawing_globals
if drawing_globals.quux_module_import_succeeded:
    import quux

from graphics.drawing.CS_ShapeList import ShapeList_inplace
from graphics.drawing.CS_workers import drawcylinder_worker
from graphics.drawing.CS_workers import drawline_worker
from graphics.drawing.CS_workers import drawpolycone_multicolor_worker
from graphics.drawing.CS_workers import drawpolycone_worker
from graphics.drawing.CS_workers import drawsphere_worker
from graphics.drawing.CS_workers import drawsurface_worker
from graphics.drawing.CS_workers import drawwiresphere_worker
from graphics.drawing.gl_lighting import apply_material

class ColorSortedDisplayList:         #Russ 080225: Added.
    """
    The ColorSorter's parent uses one of these to store color-sorted display list
    state.  It's passed in to ColorSorter.start() .
    """
    def __init__(self):
        self.clear()
        self.selected = False   # Whether to draw in the selection over-ride color.
        return

    #russ 080320 Experiment with VBO drawing from cached ColorSorter lists.
    cache_ColorSorter = False ## True

    def clear(self):
        """
        Empty state.
        """
        self.dl = 0             # Current display list (color or selected.)
        self.color_dl = 0       # DL to set colors, call each lower level list.
        self.selected_dl = 0    # DL with a single (selected) over-ride color.
        self.nocolor_dl = 0     # DL of lower-level calls for color over-rides.
        self.per_color_dls = [] # Lower level, per-color primitive sublists.
        return

    def not_clear(self):
        """
        Check for empty state.
        """
        return self.dl or self.color_dl or self.nocolor_dl or self.selected_dl or \
               self.per_color_dls and len(self.per_color_dls)

    def activate(self):
        """
        Make a top-level display list id ready, but don't fill it in.
        """
        # Display list id for the current appearance.
        if not self.selected:
            self.color_dl = glGenLists(1)
        else:
            self.selected_dl = glGenLists(1)
            pass
        self.selectDl()
        assert type(self.dl) in (type(1), type(1L)) #bruce 070521 added these two asserts
        assert self.dl != 0     # This failed on Linux, keep checking. (bug 2042)
        return

    def draw_dl(self):                  #russ 080320 Added.
        """
        Draw the displist (cached display procedure.)
        """
        #russ 080320: Experiment with VBO drawing from cached ColorSorter lists.
        if (ColorSortedDisplayList.cache_ColorSorter and
            drawing_globals.allow_color_sorting and
            drawing_globals.use_color_sorted_vbos):
            ColorSorter.draw_sorted(self.sorted_by_color)
        else:
            # Call a normal OpenGL display list.
            glCallList(self.dl)
        return

    def selectPick(self, boolVal):
        """
        Remember whether we're selected or not.
        """
        self.selected = boolVal
        self.selectDl()
        return

    def selectDl(self):
        """
        Change to either the normal-color display list or the selected one.
        """
        self.dl = self.selected and self.selected_dl or self.color_dl
        return

    def reset(self):
        """
        Return to initialized state.
        """
        if self.not_clear():
            # deallocate leaves it clear.
            self.deallocate_displists()
            pass
        return

    def deallocate_displists(self):
        """
        Free any allocated display lists.
        """
        # With CSDL active, self.dl duplicates either selected_dl or color_dl.
        if (self.dl is not self.color_dl and
            self.dl is not self.selected_dl):
            glDeleteLists(self.dl, 1)
        for dl in [self.color_dl, self.nocolor_dl, self.selected_dl]:
            if dl != 0:
                glDeleteLists(dl, 1) 
                pass
            continue
        # piotr 080420: The second level dl's are 2-element lists of DL ids 
        # rather than just a list of ids. The secod DL is used in case
        # of multi-color objects and is required for highlighting 
        # and selection (not in rc1)
        for clr, dls in self.per_color_dls: # Second-level dl's.
            for dl in dls: # iterate over DL pairs.
                if dl != 0:
                    glDeleteLists(dl, 1) 
                    pass
                continue
        self.clear()
        return

    pass # End of ColorSortedDisplayList.

class ColorSorter:

    """
    State Sorter specializing in color (Really any object that can be
    passed to apply_material, which on 20051204 is only color 4-tuples)

    Invoke start() to begin sorting.
    Call finish() to complete sorting and draw all sorted objects.

    Call schedule() with any function and parameters to be sorted by color.
    If not sorting, schedule() will invoke the function immediately.  If
    sorting, then the function will not be called until "finish()".

    In any function which will take part in sorting which previously did
    not, create a worker function from the old function except the call to
    apply_material.  Then create a wrapper which calls
    ColorSorter.schedule with the worker function and its params.

    Also an app can call schedule_sphere and schedule_cylinder to
    schedule a sphere or a cylinder.  Right now this is the only way
    to directly access the native C++ rendering engine.
    """
    __author__ = "grantham@plunk.org"

    # For now, these are class globals.  As long as OpenGL drawing is
    # serialized and Sorting isn't nested, this is okay.  When/if
    # OpenGL drawing becomes multi-threaded, sorters will have to
    # become instances.  This is probably okay because objects and
    # materials will probably become objects of their own about that
    # time so the whole system will get a redesign and
    # reimplementation.

    sorting = False     # Guard against nested sorting
    _sorted = 0         # Number of calls to _add_to_sorter since last
                        # _printstats
    _immediate = 0      # Number of calls to _invoke_immediately since last
                        # _printstats
    _gl_name_stack = [0]       # internal record of GL name stack; 0 is a sentinel

    def pushName(glname):
        """
        Record the current pushed GL name, which must not be 0.
        """
        assert glname, "glname of 0 is illegal (used as sentinel)" #bruce 060217 added this assert
        ColorSorter._gl_name_stack.append(glname)

    pushName = staticmethod(pushName)


    def popName():
        """
        Record a pop of the GL name.
        """
        del ColorSorter._gl_name_stack[-1]

    popName = staticmethod(popName)


    def _printstats():
        """
        Internal function for developers to call to print stats on number of
        sorted and immediately-called objects.
        """
        print "Since previous 'stats', %d sorted, %d immediate: " % (ColorSorter._sorted, ColorSorter._immediate)
        ColorSorter._sorted = 0
        ColorSorter._immediate = 0

    _printstats = staticmethod(_printstats)


    def _add_to_sorter(color, func, params):
        """
        Internal function that stores 'scheduled' operations for a later
        sort, between a start/finish
        """
        ColorSorter._sorted += 1
        color = tuple(color)
        if not ColorSorter.sorted_by_color.has_key(color):
            ColorSorter.sorted_by_color[color] = []
        ColorSorter.sorted_by_color[color].append((func, params,
                                                   ColorSorter._gl_name_stack[-1]))

    _add_to_sorter = staticmethod(_add_to_sorter)


    def schedule(color, func, params):
        if ColorSorter.sorting and drawing_globals.allow_color_sorting:

            ColorSorter._add_to_sorter(color, func, params)

        else:

            ColorSorter._immediate += 1 # for benchmark/debug stats, mostly

            # 20060216 We know we can do this here because the stack is
            # only ever one element deep
            name = ColorSorter._gl_name_stack[-1]
            if name:
                glPushName(name)

            #Apply appropriate opacity for the object if it is specified
            #in the 'color' param. (Also do necessary things such as 
            #call glBlendFunc it. -- Ninad 20071009

            if len(color) == 4:
                opacity = color[3]
            else:
                opacity = 1.0

            if opacity >= 0.0 and opacity != 1.0:	
                glDepthMask(GL_FALSE)
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            elif opacity == -1: 
                # piotr 080429: I replaced the " < 0" condition with " == -1"
                # The opacity flag is now used to signal either "unshaded colors"
                # (opacity == -1) or "multicolor object" (opacity == -2)
                glDisable(GL_LIGHTING)          # Don't forget to re-enable it!
                glColor3fv(color[:3])
                pass

            apply_material(color)
            func(params)

            if opacity > 0.0 and opacity != 1.0:
                glDisable(GL_BLEND)
                glDepthMask(GL_TRUE)
            elif opacity == -1: 
                # piotr 080429: See my comment above.
                glEnable(GL_LIGHTING)

            if name:
                glPopName()
        return

    schedule = staticmethod(schedule)

    def schedule_sphere(color, pos, radius, detailLevel, opacity = 1.0):
        """
        Schedule a sphere for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_sphere(lcolor, pos, radius,
                                                  ColorSorter._gl_name_stack[-1])
            # 20060208 grantham - I happen to know that one detailLevel
            # is chosen for all spheres, I just record it over and
            # over here, and use the last one for the render
            if ColorSorter.sphereLevel > -1 and ColorSorter.sphereLevel != detailLevel:
                raise ValueError, "unexpected different sphere LOD levels within same frame"
            ColorSorter.sphereLevel = detailLevel
        else: # Older sorted material rendering
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color	
            ColorSorter.schedule(lcolor, drawsphere_worker, ### drawsphere_worker_loop ### Testing.
                                 (pos, radius, detailLevel))

    schedule_sphere = staticmethod(schedule_sphere)


    def schedule_wiresphere(color, pos, radius, detailLevel = 1):
        """
        Schedule a wiresphere for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_wiresphere function."
            ColorSorter._cur_shapelist.add_wiresphere(lcolor, pos, radius,
                                                      ColorSorter._gl_name_stack[-1])
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawwiresphere_worker,
                                 # Use constant-color line drawing.
                                 (color, pos, radius, detailLevel))

    schedule_wiresphere = staticmethod(schedule_wiresphere)

    def schedule_cylinder(color, pos1, pos2, radius, capped = 0, opacity = 1.0 ):
        """
        Schedule a cylinder for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            ColorSorter._cur_shapelist.add_cylinder(lcolor, pos1, pos2, radius,
                                                    ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawcylinder_worker, (pos1, pos2, radius, capped))

    schedule_cylinder = staticmethod(schedule_cylinder)

    def schedule_polycone(color, pos_array, rad_array, capped = 0, opacity = 1.0):
        """
        Schedule a polycone for rendering whenever ColorSorter thinks is
        appropriate.
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_polycone_multicolor function."
            ColorSorter._cur_shapelist.add_polycone(lcolor, pos_array, rad_array,
                                                    ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawpolycone_worker, (pos_array, rad_array))

    schedule_polycone = staticmethod(schedule_polycone)

    def schedule_polycone_multicolor(color, pos_array, color_array, rad_array, capped = 0, opacity = 1.0):
        """
        Schedule a polycone for rendering whenever ColorSorter thinks is
        appropriate.
        piotr 080311: this variant accepts a color array as an additional parameter
        """
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            if len(color) == 3:
                lcolor = (color[0], color[1], color[2], 1.0)
            else:
                lcolor = color
            assert 0, "Need to implement a C add_polycone function."
            ColorSorter._cur_shapelist.add_polycone_multicolor(lcolor, pos_array, color_array, rad_array, 
                                                               ColorSorter._gl_name_stack[-1], capped)
        else:
            if len(color) == 3:		
                lcolor = (color[0], color[1], color[2], opacity)
            else:
                lcolor = color		    

            ColorSorter.schedule(lcolor, drawpolycone_multicolor_worker, (pos_array, color_array, rad_array))

    schedule_polycone_multicolor = staticmethod(schedule_polycone_multicolor)

    def schedule_surface(color, pos, radius, tm, nm):
        """
        Schedule a surface for rendering whenever ColorSorter thinks is
        appropriate.
        """
        ColorSorter.schedule(color, drawsurface_worker, (pos, radius, tm, nm))

    schedule_surface = staticmethod(schedule_surface)

    def schedule_line(color, endpt1, endpt2, dashEnabled,
                      stipleFactor, width, isSmooth):
        """
        Schedule a line for rendering whenever ColorSorter thinks is
        appropriate.
        """
        #russ 080306: Signal "unshaded colors" for lines by a negative alpha.  (Hack!)
        color = tuple(color) + (-1,)
        ColorSorter.schedule(color, drawline_worker,
                             (endpt1, endpt2, dashEnabled,
                              stipleFactor, width, isSmooth))

    schedule_line = staticmethod(schedule_line)

    def start(csdl, pickstate=None):
        """
        Start sorting - objects provided to "schedule", "schedule_sphere", and
        "schedule_cylinder" will be stored for a sort at the time "finish" is called.
        csdl is a ColorSortedDisplayList or None, in which case immediate drawing is done.
        pickstate (optional) indicates whether the parent is currently selected.
        """

        #russ 080225: Moved glNewList here for displist re-org.
        ColorSorter.parent_csdl = csdl  # Remember, used by finish().
        if pickstate is not None:
            csdl.selectPick(pickstate)
            pass

        if csdl != None:
            if not (drawing_globals.allow_color_sorting and
                    (drawing_globals.use_color_sorted_dls
                     or drawing_globals.use_color_sorted_vbos)): #russ 080320
                # This is the beginning of the single display list created when color
                # sorting is turned off.  It is ended in ColorSorter.finish .  In
                # between, the calls to draw{sphere,cylinder,polycone} methods pass
                # through ColorSorter.schedule_* but are immediately sent to *_worker
                # where they do OpenGL drawing that is captured into the display list.
                try:
                    if csdl.dl is 0:
                        csdl.activate()             # Allocate a display list for our use.
                        pass
                    glNewList(csdl.dl, GL_COMPILE_AND_EXECUTE) # Start a single-level list.
                except:
                    print "data related to following exception: csdl.dl = %r" % (csdl.dl,) #bruce 070521
                    raise

        assert not ColorSorter.sorting, "Called ColorSorter.start but already sorting?!"
        ColorSorter.sorting = True
        if drawing_globals.use_c_renderer and ColorSorter.sorting:
            ColorSorter._cur_shapelist = ShapeList_inplace()
            ColorSorter.sphereLevel = -1
        else:
            ColorSorter.sorted_by_color = {}

    start = staticmethod(start)

    def finish():
        """
        Finish sorting - objects recorded since "start" will
        be sorted and invoked now.
        """
        from utilities.debug_prefs import debug_pref, Choice_boolean_False
        debug_which_renderer = debug_pref("debug print which renderer", Choice_boolean_False) #bruce 060314, imperfect but tolerable

        parent_csdl = ColorSorter.parent_csdl
        if drawing_globals.use_c_renderer:
            quux.shapeRendererInit()
            if debug_which_renderer:
                #bruce 060314 uncommented/revised the next line; it might have to come after shapeRendererInit (not sure);
                # it definitely has to come after a graphics context is created and initialized.
                # 20060314 grantham - yes, has to come after quux.shapeRendererInit
                print "using C renderer: VBO %s enabled" % (('is NOT', 'is')[quux.shapeRendererGetInteger(quux.IS_VBO_ENABLED)])
            quux.shapeRendererSetUseDynamicLOD(0)
            if ColorSorter.sphereLevel != -1:
                quux.shapeRendererSetStaticLODLevels(ColorSorter.sphereLevel, 1)
            quux.shapeRendererStartDrawing()
            ColorSorter._cur_shapelist.draw()
            quux.shapeRendererFinishDrawing()
            ColorSorter.sorting = False

            # So chunks can actually record their shapelist
            # at some point if they want to
            # ColorSorter._cur_shapelist.petrify()
            # return ColorSorter._cur_shapelist      

        else:
            if debug_which_renderer:
                print "using Python renderer: use_color_sorted_dls %s enabled" \
                      % (drawing_globals.use_color_sorted_dls and 'IS'
                         or 'is NOT')
                print "using Python renderer: use_color_sorted_vbos %s enabled" \
                      % (drawing_globals.use_color_sorted_vbos and 'IS'
                         or 'is NOT')
            color_groups = len(ColorSorter.sorted_by_color)
            objects_drawn = 0

            if (not (drawing_globals.allow_color_sorting and
                     drawing_globals.use_color_sorted_dls)
                or (ColorSortedDisplayList.cache_ColorSorter and
                    drawing_globals.allow_color_sorting and
                    drawing_globals.use_color_sorted_vbos)
                or parent_csdl is None):  #russ 080225 Added, 080320 VBO experiment.

                # Either all in one display list, or immediate-mode drawing.
                objects_drawn += ColorSorter.draw_sorted(ColorSorter.sorted_by_color)

                #russ 080225: Moved glEndList here for displist re-org.
                if parent_csdl is not None:
                    #russ 080320: Experiment with VBO drawing from cached ColorSorter lists.
                    if (ColorSortedDisplayList.cache_ColorSorter and
                        drawing_globals.allow_color_sorting and
                        drawing_globals.use_color_sorted_vbos):
                        # Remember the ColorSorter lists for use as a pseudo-display-list.
                        parent_csdl.sorted_by_color = ColorSorter.sorted_by_color
                    else:
                        # Terminate a single display list, created when color sorting
                        # is turned off.  It was started in ColorSorter.start .
                        glEndList()
                    pass
                pass

            else: #russ 080225

                parent_csdl.reset()

                # First build the lower level per-color sublists of primitives.
                for color, funcs in ColorSorter.sorted_by_color.iteritems():
                    sublists = [glGenLists(1), 0]

                    # Remember the display list ID for this color.
                    parent_csdl.per_color_dls.append([color, sublists])

                    glNewList(sublists[0], GL_COMPILE)
                    opacity = color[3]

                    if opacity == -1:
                        #russ 080306: "Unshaded colors" for lines are signaled
                        # by an opacity of -1 (4th component of the color.)
                        glDisable(GL_LIGHTING) # Don't forget to re-enable it!
                        pass

                    for func, params, name in funcs:
                        objects_drawn += 1
                        if name != 0:
                            glPushName(name)
                        func(params)
                        if name != 0:
                            glPopName()
                            pass
                        continue

                    if opacity == -1:
                        # Enable lighting after drawing "unshaded" objects.
                        glEnable(GL_LIGHTING)
                        pass
                    glEndList()

                    if opacity == -2:
                        # piotr 080419: Special case for drawpolycone_multicolor
                        # create another display list that ignores
                        # the contents of color_array.
                        # Remember the display list ID for this color.

                        sublists[1] = glGenLists(1)

                        glNewList(sublists[1], GL_COMPILE)

                        for func, params, name in funcs:
                            objects_drawn += 1
                            if name != 0:
                                glPushName(name)
                            pos_array, color_array, rad_array = params
                            if func == drawpolycone_multicolor_worker:
                                # Just to be sure, check if the func
                                # is drawpolycone_multicolor_worker
                                # and call drawpolycone_worker instead.
                                # I think in the future we can figure out 
                                # a more general way of handling the 
                                # GL_COLOR_MATERIAL objects. piotr 080420
                                drawpolycone_worker((pos_array, rad_array))
                            if name != 0:
                                glPopName()
                                pass
                            continue
                        glEndList()

                    continue

                # Now the upper-level lists call all of the per-color sublists.
                # One with colors.
                color_dl = parent_csdl.color_dl = glGenLists(1)
                glNewList(color_dl, GL_COMPILE)

                for color, dls in parent_csdl.per_color_dls:

                    opacity = color[3]
                    if opacity < 0:
                        #russ 080306: "Unshaded colors" for lines are signaled
                        # by a negative alpha.
                        glColor3fv(color[:3])
                        # piotr 080417: for opacity == -2, i.e. if
                        # GL_COLOR_MATERIAL is enabled, the color is going 
                        # to be ignored, anyway, so it is not necessary
                        # to be tested here
                    else:
                        apply_material(color)

                    glCallList(dls[0])

                    continue
                glEndList()

                # A second one without any colors.
                nocolor_dl = parent_csdl.nocolor_dl = glGenLists(1)
                glNewList(nocolor_dl, GL_COMPILE)
                for color, dls in parent_csdl.per_color_dls:                    
                    opacity = color[3]

                    if opacity == -2 \
                       and dls[1] > 0:
                        # piotr 080420: If GL_COLOR_MATERIAL is enabled,
                        # use a regular, single color dl rather than the
                        # multicolor one. Btw, dls[1] == 0 should never 
                        # happen.
                        glCallList(dls[1])
                    else:
                        glCallList(dls[0])

                glEndList()

                # A third overlays the second with a single color for selection.
                selected_dl = parent_csdl.selected_dl = glGenLists(1)
                glNewList(selected_dl, GL_COMPILE)
                apply_material(darkgreen)
                glCallList(nocolor_dl)
                glEndList()

                # Use either the normal-color display list or the selected one.
                parent_csdl.selectDl()

                # Draw the newly-built display list.
                parent_csdl.draw_dl()
                pass

            ColorSorter.sorted_by_color = None
            pass
        ColorSorter.sorting = False
        return

    finish = staticmethod(finish)

    def draw_sorted(sorted_by_color):     #russ 080320: factored out of finish().
        """
        Traverse color-sorted lists, invoking worker procedures.
        """
        objects_drawn = 0               # Keep track and return.
        glEnable(GL_LIGHTING)

        for color, funcs in sorted_by_color.iteritems():

            opacity = color[3]
            if opacity == -1:
                #piotr 080429: Opacity == -1 signals the "unshaded color".
                # Also, see my comment in "schedule".
                glDisable(GL_LIGHTING) # Don't forget to re-enable it!
                glColor3fv(color[:3])
            else:
                apply_material(color)
                pass

            for func, params, name in funcs:
                objects_drawn += 1
                if name != 0:
                    glPushName(name)
                func(params)
                if name != 0:
                    glPopName()
                    pass
                continue

            if opacity == -1:
                glEnable(GL_LIGHTING)

            continue
        return objects_drawn

    draw_sorted = staticmethod(draw_sorted)

    pass # End of class ColorSorter.
