#!/usr/bin/python
# -*- coding: utf-8 -*-

import gtk
from board import *

# ******************************************************************************
# ************************************************************************ PyRob
# ******************************************************************************
class PyRob(object):
    """Application pour Ricochet Robot
    """
    
    # --------------------------------------------------------------------- init
    def __init__(self, ):
        """Crée une fenetre avec Board et Boutons
        """
        # Board
        self._board = create_board16()
        self._btree = ReachTree( self._board, "tb" )
        self._board._tree.append( self._btree )
        #
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title( "Ricochet Robots" )
        window.resize(750,600)
        window.connect("delete-event", gtk.main_quit)
        #
        widget = self.build_gui()
        window.add( widget )
        widget.show()
        #
        window.present()
        gtk.main()

    # ---------------------------------------------------------------- build_gui
    def build_gui(self, ):
        """
        HBox { Board, VBox}
        VBox { {btn for bsearch }
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
        reset_btn.connect( "clicked", self.bsearch_reset_cbk, "Reset_BT")
        btn_vbox.pack_start(reset_btn, expand=False, fill=False, padding=0)
        reset_btn.show()
        self._bsearch_step_btn = gtk.Button("Step")
        self._bsearch_step_btn.connect( "clicked", self.bsearch_step_cbk, "Step_BT")
        self._bsearch_step_btn.set_sensitive( False )
        btn_vbox.pack_start(self._bsearch_step_btn, expand=False, fill=False, padding=0)
        self._bsearch_step_btn.show()
        value_btn = gtk.CheckButton("valeurs")
        value_btn.set_active( self._btree._draw_value )
        value_btn.connect( "toggled", self.bsearch_valeur_cbk, "Valeur_BT")
        btn_vbox.pack_start(value_btn, expand=False, fill=False, padding=0)
        value_btn.show()
        arc_btn = gtk.CheckButton("arcs")
        arc_btn.set_active( self._btree._draw_arc )
        arc_btn.connect( "toggled", self.bsearch_arc_cbk, "Arc_BT")
        btn_vbox.pack_start(arc_btn, expand=False, fill=False, padding=0)
        arc_btn.show()
        
        # 
        separator = gtk.HSeparator()
        btn_vbox.pack_start(separator, expand=False, fill=True, padding=5)
        separator.show()
        
        return main_hbox
    # --------------------------------------------------------------- bbasic_cbk
    def bbasic_cbk(self, widget, data=None):
        """Callbak de base pour bouton
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._board.queue_draw()
    # -------------------------------------------------------- bsearch_reset_cbk
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
        if len(self._btree._cell_to_expand) > 0 :
            self._bsearch_step_btn.set_sensitive( True )
        self._board.queue_draw()
    # --------------------------------------------------------- bsearch_step_cbk
    def bsearch_step_cbk(self, widget, data=None):
        """Un step de recherche
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._btree.expand_step()
        print "Il reste {0} cell à explorer".format(len(self._btree._cell_to_expand))
        if len(self._btree._cell_to_expand) == 0 :
            self._bsearch_step_btn.set_sensitive( False )
        self._board.queue_draw()
    # ------------------------------------------------------- bsearch_valeur_cbk
    def bsearch_valeur_cbk(self, widget, data=None):
        """Affiche ou non les valeurs du Tree de recherche en largeur
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._btree._draw_value = widget.get_active()
        self._board.queue_draw()
    # ---------------------------------------------------------- bsearch_arc_cbk
    def bsearch_arc_cbk(self, widget, data=None):
        """Affiche ou non les arcs du Tree de recherche en largeur
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._btree._draw_arc = widget.get_active()
        self._board.queue_draw()

        

# ******************************************************************************
# ************************************************************************** END
# ******************************************************************************

if __name__ == '__main__':
    app = PyRob()

