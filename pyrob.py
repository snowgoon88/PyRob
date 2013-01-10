#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
from board import *

# ******************************************************************************
# ************************************************************************* TODO
# ******************************************************************************
class PyRob(object):
    """Application pour Ricochet Robot
    """
    
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def __init__(self, ):
        """
        """
        # Board
        self._board = create_board16()
        self._btree = ReachTree( self._board, "tb" )
        self._board._tree.append( self._btree )
        #
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.resize(750,600)
        window.connect("delete-event", gtk.main_quit)
        #
        widget = self.build_gui()
        window.add( widget )
        widget.show()
        #
        window.present()
        gtk.main()
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def build_gui(self, ):
        """
        HBox { Board, VBox}
        VBox { reset_btn, step_btn }
        """
        main_hbox = gtk.HBox(homogeneous=False, spacing=0)
        main_hbox.pack_start(self._board, expand=True, fill=True, padding=0)
        self._board.show()
        # Button
        btn_vbox = gtk.VBox(homogeneous=False, spacing=0)
        main_hbox.pack_start(btn_vbox, expand=False, fill=True, padding=10)
        btn_vbox.show()
        label = gtk.Label("Recherche LARGEUR")
        btn_vbox.pack_start(label, expand=False, fill=False, padding=0)
        label.show()
        reset_btn = gtk.Button("Reset")
        reset_btn.connect( "clicked", self.bsearch_reset_cbk, "Reset")
        btn_vbox.pack_start(reset_btn, expand=False, fill=False, padding=0)
        reset_btn.show()
        step_btn = gtk.Button("Step")
        step_btn.connect( "clicked", self.bsearch_step_cbk, "Step")
        btn_vbox.pack_start(step_btn, expand=False, fill=False, padding=0)
        step_btn.show()
        
        # 
        separator = gtk.HSeparator()
        btn_vbox.pack_start(separator, expand=False, fill=True, padding=5)
        separator.show()
        
        return main_hbox
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def bsearch_reset_cbk(self, widget, data=None):
        """Remet à zéro la recherche en profondeur.
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._btree.clean()
        self._btree.build_step( (0,0) )
        print "Il reste {0} cell à explorer".format(len(self._btree._cell_to_expand))
        self._board.queue_draw()
    def bsearch_step_cbk(self, widget, data=None):
        """Un step de recherche
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._btree.expand_step()
        print "Il reste {0} cell à explorer".format(len(self._btree._cell_to_expand))
        self._board.queue_draw()
# ******************************************************************************
# ************************************************************************* TODO
# ******************************************************************************

if __name__ == '__main__':
    app = PyRob()

