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
        rob = Robot( self._board, col=(1,0,0), label="rr")
        self._board._robot.append(rob)
        rob.put( (7,7) )
        rob = Robot( self._board, col=(0,0,1), label="rb")
        self._board._robot.append(rob)
        rob.put( (7,8) )
        rob = Robot( self._board, col=(0,1,0), label="rg")
        self._board._robot.append(rob)
        rob.put( (8,7) )
        rob = Robot( self._board, col=(0.9,0.9,0), label="ry")
        self._board._robot.append(rob)
        rob.put( (8,8) )
        self._board._robot_to_move = 0
        self._board._target = Target( self._board, label="ta" )

        self._btree = BroadTree( self._board, "tb" )
        self._board._tree.append( self._btree )
        self._dtree = DepthTree( self._board, "td" )
        self._board._tree.append( self._dtree )
        self._atree = AStar( self._board, "ta" )
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
        # VBOX Buttons ---------------
        btn_vbox = gtk.VBox(homogeneous=False, spacing=0)
        main_hbox.pack_start(btn_vbox, expand=False, fill=True, padding=10)
        btn_vbox.show()

        ## Recherche en largeur
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

        ## Recherche en profondeur
        label = gtk.Label("Recherche PROFONDEUR")
        btn_vbox.pack_start(label, expand=False, fill=False, padding=0)
        label.show()
        reset_btn = gtk.Button("Reset")
        reset_btn.connect( "clicked", self.dsearch_reset_cbk, "Reset_DT")
        btn_vbox.pack_start(reset_btn, expand=False, fill=False, padding=0)
        reset_btn.show()
        self._dsearch_step_btn = gtk.Button("Step")
        self._dsearch_step_btn.connect( "clicked", self.dsearch_step_cbk, "Step_DT")
        self._dsearch_step_btn.set_sensitive( False )
        btn_vbox.pack_start(self._dsearch_step_btn, expand=False, fill=False, padding=0)
        self._dsearch_step_btn.show()
        value_btn = gtk.CheckButton("valeurs")
        value_btn.set_active( self._dtree._draw_value )
        value_btn.connect( "toggled", self.dsearch_valeur_cbk, "Valeur_DT")
        btn_vbox.pack_start(value_btn, expand=False, fill=False, padding=0)
        value_btn.show()
        arc_btn = gtk.CheckButton("arcs")
        arc_btn.set_active( self._dtree._draw_arc )
        arc_btn.connect( "toggled", self.dsearch_arc_cbk, "Arc_DT")
        btn_vbox.pack_start(arc_btn, expand=False, fill=False, padding=0)
        arc_btn.show()
        # 
        separator = gtk.HSeparator()
        btn_vbox.pack_start(separator, expand=False, fill=True, padding=5)
        separator.show()



        ## Cycles
        label = gtk.Label("Cycles")
        btn_vbox.pack_start(label, expand=False, fill=False, padding=0)
        label.show()
        arc_btn = gtk.CheckButton("arcs")
        arc_btn.set_active( self._board._fg_draw_cycles )
        arc_btn.connect( "toggled", self.cycles_arc_cbk, "Arc_CY")
        btn_vbox.pack_start(arc_btn, expand=False, fill=False, padding=0)
        arc_btn.show()
        update_btn = gtk.Button("Update")
        update_btn.connect( "clicked", self.cycles_update_cbk, "Update_CY")
        btn_vbox.pack_start(update_btn, expand=False, fill=False, padding=0)
        update_btn.show()
        # 
        separator = gtk.HSeparator()
        btn_vbox.pack_start(separator, expand=False, fill=True, padding=5)
        separator.show()

        ## Robots
        label = gtk.Label("Robots/Target")
        btn_vbox.pack_start(label, expand=False, fill=False, padding=0)
        label.show()
        rob_hbox = gtk.HBox(homogeneous=False, spacing=0)
        redr_btn = gtk.RadioButton(None,"R")
        redr_btn.connect( "toggled", self.choose_rob_cbk, "rr")
        rob_hbox.pack_start(redr_btn, expand=False, fill=False, padding=0)
        redr_btn.show()
        bluer_btn = gtk.RadioButton(redr_btn, "B")
        bluer_btn.connect( "toggled", self.choose_rob_cbk, "rb")
        rob_hbox.pack_start(bluer_btn, expand=False, fill=False, padding=0)
        bluer_btn.show()
        greenr_btn = gtk.RadioButton(bluer_btn, "V")
        greenr_btn.connect( "toggled", self.choose_rob_cbk, "rg")
        rob_hbox.pack_start(greenr_btn, expand=False, fill=False, padding=0)
        greenr_btn.show()
        yellowr_btn = gtk.RadioButton(greenr_btn, "J")
        yellowr_btn.connect( "toggled", self.choose_rob_cbk, "ry")
        rob_hbox.pack_start(yellowr_btn, expand=False, fill=False, padding=0)
        yellowr_btn.show()
        target_btn = gtk.RadioButton(yellowr_btn, "T")
        target_btn.connect( "toggled", self.choose_rob_cbk, "rt")
        rob_hbox.pack_end(target_btn, expand=False, fill=False, padding=0)
        target_btn.show()

        btn_vbox.pack_start(rob_hbox, expand=False, fill=False, padding=0)
        rob_hbox.show()
        # 
        separator = gtk.HSeparator()
        btn_vbox.pack_start(separator, expand=False, fill=True, padding=5)
        separator.show()

        ## AStar
        label = gtk.Label("A*")
        btn_vbox.pack_start(label, expand=False, fill=False, padding=0)
        label.show()
        astar_adjustment = gtk.Adjustment(value=500, lower=0, upper=10000, step_incr=100, page_incr=1000, page_size=0)
        self._astar_button = gtk.SpinButton(adjustment=astar_adjustment, climb_rate=0.8, digits=0)
        btn_vbox.pack_start(self._astar_button, expand=False, fill=False, padding=0)
        self._astar_button.show()
        self._averb_btn = gtk.ToggleButton("verbeux")
        btn_vbox.pack_start(self._averb_btn, expand=False, fill=False, padding=0)
        self._averb_btn.show()
        reset_btn = gtk.Button("Reset")
        reset_btn.connect( "clicked", self.asearch_reset_cbk, "Reset_AT")
        btn_vbox.pack_start(reset_btn, expand=False, fill=False, padding=0)
        reset_btn.show()
        self._asearch_run_btn = gtk.Button("Run")
        self._asearch_run_btn.connect( "clicked", self.asearch_run_cbk, "Run_AT")
        #self._asearch_run_btn.set_sensitive( False )
        btn_vbox.pack_start(self._asearch_run_btn, expand=False, fill=False, padding=0)
        self._asearch_run_btn.show()
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

    # ----------------------------------------------------------- cycles_atc_cbk
    def cycles_arc_cbk(self, widget, data=None):
        """Affiche ou non les arcs des Cycles
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._board._fg_draw_cycles = widget.get_active()
        self._board.queue_draw()
    # -------------------------------------------------------- cycles_update_cbk
    def cycles_update_cbk(self, widget, data=None):
        """Reconstruits les cycles de _board
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._board.clean_cycles()
        self._board.build_basic_cycles()
        self._board.queue_draw()
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def dsearch_reset_cbk(self, widget, data=None):
        """Remet à zéro la recherche en largeur.
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._dtree.clean()
        self._dtree.build_step( (0,0) )
        self._dsearch_step_btn.set_sensitive( True )
        print "path=",self._dtree._path," : ",self._dtree._path_ind,"/",len(self._dtree._path)
        self._board.queue_draw()
    # --------------------------------------------------------- dsearch_step_cbk
    def dsearch_step_cbk(self, widget, data=None):
        """Un step de recherche en profondeur
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        res = self._dtree.expand_step()
        print "path=",self._dtree._path," : ",self._dtree._path_ind,"/",len(self._dtree._path)
        self._dsearch_step_btn.set_sensitive( res )
        self._board.queue_draw()
    # ------------------------------------------------------- dsearch_valeur_cbk
    def dsearch_valeur_cbk(self, widget, data=None):
        """Affiche ou non les valeurs du Tree de recherche en profondeur
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._dtree._draw_value = widget.get_active()
        self._board.queue_draw()
    # ---------------------------------------------------------- dsearch_arc_cbk
    def dsearch_arc_cbk(self, widget, data=None):
        """Affiche ou non les arcs du Tree de recherche en largeur
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._dtree._draw_arc = widget.get_active()
        self._board.queue_draw()
    # --------------------------------------------------------------------- todo
    def choose_rob_cbk(self, widget, data=None):
        """Choisi quel robot/target a mettre/enlever sur le Board.
        :Param
        - `widget`: source
        - `data`: extra data
        """
        # print "btn  {0} pressed".format(data)
        # Faut trouver le bon robot
        self._board._robot_to_move = None
        # Si on trouve un robot => son indice, sinon reste None
        for i_rob in xrange(len(self._board._robot)):
            if self._board._robot[i_rob]._label == data:
                self._board._robot_to_move = i_rob
        print self._board._robot_to_move
        # self._board.queue_draw()
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def asearch_reset_cbk(self, widget, data=None):
        """Callbak de base pour bouton
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        self._atree.reset_search()
        #self._board.queue_draw()
    def asearch_run_cbk(self, widget, data=None):
        """Callbak de base pour bouton
        :Param
        - `widget`: source
        - `data`: extra data
        """
        print "btn  {0} pressed".format(data)
        max_iteration = self._astar_button.get_value_as_int()
        path = self._atree.search( max_iteration, verb=self._averb_btn.get_active())
        if path != None :
            print "**** Solution trouvée ***"
            print str([s.__str__() for s in path])
        else:
            print ".... Pas de solution..."
            print self._atree.dump_closed()
        print "CLOSED a ",len(self._atree._closed)," noeuds"
        print "OPEN a ",len(self._atree._open)," noeuds"
        #self._board.queue_draw()
        

# ******************************************************************************
# ************************************************************************** END
# ******************************************************************************

if __name__ == '__main__':
    app = PyRob()

