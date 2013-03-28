# -*- coding: utf-8 -*-

# Le mieux est d'utiliser ipython avec le thread de gtk
# ipython -gthread
# xfce4-terminal -e "ipython -gthread"
# ou, dans une version plus récente,
# xfce4-terminal -e "ipython --gui=gtk "
#
# Exemple de run
# >> bb = create_board5()
# >> affiche(bb)
# >> t = BroadTree( bb, "t1" )
# >> t._draw_value = True # aussi valeurs des cases
# >> bb._tree.append( t )
# >> t.clean()
# >> t.build( (0,1), 6)
# >> bb.draw_queue()
# >> t.clean()
# >> t.build( (0,1), 3)
# >> bb.draw_queue()
# >> bb.detect_corners()
# >> c = Cycle(bb, "c1")
# >> c.build_from_corner( (4,0), 3)
# >> bb._cycles.append( t )
# >> bb.draw_queue()


import pygtk
import gtk, gobject, cairo
from robot import *
from cell import *
from search import *
import copy
import math

# ******************************************************************************
# ************************************************************************ Board
# ******************************************************************************
class Grafik(object):
    """
    Quelques facilité pour le graphisme.
    """
    _colors = [ (1,0,0), (0,1,0), (0,0,1), (0.9,0.9,0), (1,0,1), (0,1,1) ]

    # --------------------------------------------------------------------- init
    def __init__(self, ):
        """
        Rien de spécial
        """
        pass

# ******************************************************************************
# ************************************************************************ Board
# ******************************************************************************
class Board( gtk.DrawingArea ):
    """
    Board est une grille de _size x _size.
    Les murs verticaux et horizontaux sont dans _ver_wall et _hor_wall.
    0,0 est en bas à gauche.
    Pour chaque ligne, la position des murs verticaux [2,9,13] signifie à gauche des cases .,2, .,9 et .,13.
    Pour chaque colonne, la position des murs horizontaux [2,14] signifie en bas des cases 2,. et 14,.
    """
    # --------------------------------------------------------------------- init
    def __init__(self, size, vert_wall = [], hor_wall = [] ):
        """
        Initialise la Board de taille size x size. Crée les Cell
        No Cycles, Tree, Robots.
        :Param
        - size Taille d'un coté de la Board
        """
        gtk.DrawingArea.__init__(self)
        print "Board.__init__"
        self._go = {'Right':self.go_right, 'Left':self.go_left,
                    'Up':self.go_up, 'Down':self.go_down}

        self._size = size
        self._ver_wall = vert_wall
        self._hor_wall = hor_wall
        # Crée toutes les Cell
        self._cells = {}
        for x in range(self._size):
            for y in range(self._size):
                self._cells[ (x,y) ] = Cell( (x,y) )

        self._cycles = []
        self._tree = []
        self._robot = []
        self._robot_to_move = None
        self._target = None
        # What to draw
        self._fg_draw_cycles = True

        # no handle to the function called in idle.
        self.idleWork = -1
        self.set_idle( False ) 

        #self.mtrx = cairo.Matrix(fx,0,0,fy,cx*(1-fx),cy*(fy-1))
        self.mtrx = cairo.Matrix(1,0,0,-1, 0, 0 )

        self.add_events( gtk.gdk.BUTTON_PRESS_MASK )
        self.connect("expose-event", self.draw_cbk )
        self.connect("button-press-event", self.click_cbk)

    # ----------------------------------------------------------------- set_idle
    def set_idle(self, flag):
        """
        True pour dessiner en idle, False sinon.
        """
        if( flag ) :
            if( self.idleWork == -1) :
                self.idleWork = gobject.idle_add( self.idle_callback )
        else :
            if( self.idleWork != -1) :
                gobject.source_remove( self.idleWork )
                self.idleWork = -1

    # --------------------------------------------------------------- draw_board
    def draw_board( self, cr ):
        """
        Dessine la grille de _size x _size, avec des bords épais.
        En noir.
        :Param
        - cr Cairo Context
        """
        # TODO Devrait choisir l'épaisseur et la couleur
        # Noir
        cr.set_source_rgb( 0, 0, 0)
        # dessine intérieur en ligne fine
        cr.set_line_width(0.02)
        for pos in range(self._size+1):
            cr.move_to( -0.5, pos-0.5 )
            cr.line_to( self._size-0.5, pos-0.5 )
            cr.move_to( pos-0.5, -0.5 )
            cr.line_to( pos-0.5, self._size-0.5 )
        cr.stroke()
        # dessine bord en ligne épaisse
        cr.set_line_width(0.1)
        cr.move_to( -0.5, -0.5 )
        cr.rel_line_to( self._size, 0 )
        cr.rel_line_to( 0, self._size )
        cr.rel_line_to( -self._size, 0)
        cr.rel_line_to( 0, -self._size )
        cr.stroke()
    # --------------------------------------------------------------- draw_walls
    def draw_walls(self, cr):
        """
        En utilisant _ver_wall et _hor_wall, dessine les murs en traits épais.
        :Param
        - cr Cairo Context
        """
        # TODO Devrait choisir l'épaisseur et la couleur
        # Noir
        cr.set_source_rgb( 0, 0, 0)
        cr.set_line_width(0.1)
        # Hor and vert
        for i in range(self._size):
            for x in self._ver_wall[i]:
                cr.move_to( x-0.5, i-0.5)
                cr.rel_line_to( 0, 1)
                cr.stroke()
            for y in self._hor_wall[i]:
                cr.move_to( i-0.5, y-0.5)
                cr.rel_line_to( 1, 0)
                cr.stroke()
    # ---------------------------------------------------------------- draw_axes
    def draw_axes(self, cr):
        """
        Dessine les axes en gris
        :Param
        - cr Cairo Context
        """
        # en gris
        cr.set_line_width(0.02)
        cr.set_source_rgb(0.3, 0.3, 0.3)
        cr.move_to( -1,0 )
        cr.line_to( 1,0 )
        cr.move_to( 0, -1 )
        cr.line_to( 0, 1 )
        cr.stroke()
        #self.draw_value( cr, "0", 0, 0 )
        #self.draw_value( cr, "1", 5-0.3, 0 )
        #self.draw_value( cr, "2", 2+0.3, 4-0.5 )
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def draw_value( self, cr, txt, pos_x, pos_y):
        cr.set_font_size(0.4)
        x_bearing, y_bearing, width, height = cr.text_extents( txt )[:4]
        cr.move_to(pos_x - width / 2 - x_bearing, pos_y - height / 2 - y_bearing)
        cr.save()
        cr.transform( self.mtrx )
        cr.show_text(txt)
        cr.restore()
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def draw_cycles(self, cr):
        for cy in self._cycles:
            cy.draw( cr )
    # --------------------------------------------------------------- draw_trees
    def draw_trees(self, cr):
        """
        Dessine tous les arbres attachés.
        :Param
        - cr Cairo Context
        """
        for t in self._tree:
            t.draw( cr )
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def draw_robots(self, cr):
        """
        Dessine tous les robots attachés.
        :Param
        - cr Cairo Context
        """
        for r in self._robot:
            r.draw( cr )
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def draw_target(self, cr):
        """
        Dessine la Target
        :Param
        - cr Cairo Context
        """
        if self._target != None:
            self._target.draw( cr )
    # --------------------------------------------------------------------- draw
    def draw(self, cr, width, height):
        """
        Remplis le canevas de la couleur de fond (gris),
        puis dessine tout (axes, board, walls, cycles, tree, ...)
        :Param
        - cr Cairo Context
        - width du canevas Cairo
        - height du canevas Cairo
        """
        # Fill the background with white
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        # set up a transform so that board (0,0) x (_size,_size)
        # maps to (0,0)x(width, height)
        # with a margin of 1.0
        cr.scale(width / (self._size + 2.0),
                 -height / (self._size + 2.0) )
        cr.translate( 1.5 , -self._size-0.5 )
        # draw
        # self.draw_axes(cr)
        self.draw_board(cr)
        self.draw_walls(cr)
        if self._fg_draw_cycles :
            self.draw_cycles(cr)
        self.draw_trees(cr)
        self.draw_robots(cr)
        self.draw_target(cr)
    # ----------------------------------------------------------------- draw_cbk
    def draw_cbk( self, widget, event ):
        """
        Dessine tout.
        Callback de gtk.DrawingArea.
        """
        # print "Board.draw_cbk"
        # Create the cairo context
        cr = self.window.cairo_create()
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()
        #
        self.draw(cr, *self.window.get_size())
        return True

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def click_on_cell(self, pos_x, pos_y):
        """Enlève le robot s'il est sur la Cell, ajoute sinon.
        :Param
        - `pos_x,pos_y`: position cliquée
        """
        if self._robot_to_move != None:
            cell_here = self.get_cell( (pos_x,pos_y))
            if cell_here._rob == self._robot[self._robot_to_move]:
                self._robot[self._robot_to_move].remove();
            else:
                self._robot[self._robot_to_move].remove()
                self._robot[self._robot_to_move].put( (pos_x,pos_y) )
        else:
            # Move the target
            self._target.put( (pos_x,pos_y) )
        #
        #self.clean_cycles()
        #self.build_basic_cycles()
        #
        self.queue_draw()

    # ---------------------------------------------------------------- click_cbk
    def click_cbk( self, widget, event ):
        """
        Affiche 'event' et coordonnées de la souris.
        Callback de gtk.DrawingArea.
        """
        width,height = self.window.get_size()
        pos_x = (int) (event.x*(self._size+2.0)/width-1.0)
        pos_y = (int) ((height-event.y)*(self._size+2.0)/height-1.0)
        # print event," x=",event.x," (",event.x*(self._size+2.0)/width-1.0,") y=",event.y," (",(height-event.y)*(self._size+2.0)/height-1.0,")"
        # print "pos = {0},{1}".format(pos_x,pos_y)
        #
        # Action
        self.click_on_cell( pos_x, pos_y )

    # ------------------------------------------------------------ idle_callback
    def idle_callback(self):
        """
        Fonction qui peut être appelée à chaque fois que Cairo/GTK est idle.
        """
        #print "Idle"
        return True

    # ----------------------------------------------------------------- go_right
    def go_right( self, pos_x, pos_y ):
        """
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._ver_wall[pos_y]
        # pos : position murs, extremite et éventuels robots
        pos = [p for p in walls if p>pos_x]+[self._size]+[r._pos[0] for r in self._robot if (r._pos[1] == pos_y and r._pos[0]>pos_x)]
        return (min(pos)-1,pos_y)
    # ------------------------------------------------------------------ go_left
    def go_left( self, pos_x, pos_y ):
        """
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._ver_wall[pos_y]
        # pos : position murs, extremite et éventuels robots
        pos = [p for p in walls if p<=pos_x]+[0]+[r._pos[0]+1 for r in self._robot if (r._pos[1] == pos_y and r._pos[0]<pos_x)]
        return (max(pos),pos_y)
    # -------------------------------------------------------------------- go_up
    def go_up( self, pos_x, pos_y ):
        """
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._hor_wall[pos_x]
        # pos : position murs, extremite et éventuels robots
        pos = [p for p in walls if p>pos_y]+[self._size]+[r._pos[1] for r in self._robot if (r._pos[0] == pos_x and r._pos[1]>pos_y)]
        return (pos_x,min(pos)-1)
    # ------------------------------------------------------------------ go_down
    def go_down( self, pos_x, pos_y ):
        """
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._hor_wall[pos_x]
        # pos : position murs, extremite et éventuels robots
        pos = [p for p in walls if p<=pos_y]+[0]+[r._pos[1]+1 for r in self._robot if (r._pos[0] == pos_x and r._pos[1]<pos_y)]
        return (pos_x,max(pos))

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def build_basic_cycles(self, ):
        """
        Recherche tous les cycles présents sur le Board.
        """
        # D'abord où sont les coins
        corners = self.detect_corners()
        # Effacer tous les cycles
        self._cycles = []
        # Si possible, un cycle pour chacun de ces coins
        for coin in corners:
            print "Corner : ",coin
            # TODO Déjà dans un cycle ?
            cn = self.get_cycle( coin._pos )
            if len(cn) == 0 and not coin.has_rob():
                print " build cycle..."
                # Faire un nouveau cycle
                cyc = Cycle( self, 'c'+str(len(self._cycles)) )
                cyc.build_from_corner( coin._pos, 15 )
                print cyc
                cyc._color = Grafik._colors[len(self._cycles) % len(Grafik._colors)]
                self._cycles.append( cyc )
        print "Trouvé ",len(self._cycles)," cycles"
    # --------------------------------------------------------------------- todo
    def check_cycle_extremities(self, ):
        """
        Vérifie que les extrémités des Cycles sont bien sur d'autres Cycles.
        """
        # TODO Faire une liste des points extrémités, et dépiler cette liste
        # TODO au fur et à mesure. Cela évitera de tester ds 'build_perpendi...'
        # TODO Faut faire des Pop et Push.
        # Cycles
        for cyc in self._cycles:
            for ext in cyc._ext:
                # Nombre de tag qui commencent par "c"
                l_tag = []
                for tag in ext._values.keys():
                    if tag.startswith('c'):
                        l_tag.append( tag )
                # Devrait y avoir 2 cycles.
                if len(l_tag) == 1:
                    print ext," has ",len(l_tag)
                    # Si 3 direction, Cycle boucle sur lui même. Pas grave
                    # Si 1 direction, ajouter un Cycle qui croise.
                    if len(ext._values[l_tag[0]]) == 1:
                        new_cycle = Cycle( self, 'c'+str(len(self._cycles)) )
                        print " build cycle perp to ",ext._values[l_tag[0]][0]," from ",ext._pos
                        res = new_cycle.build_perpendicular_to(ext._pos, ext._values[l_tag[0]][0])
                        if res is not None:
                            print new_cycle
                            # TODO Verifier que les extrémités ne sont pas à augmenter
                            # TODO Renvooyer extrémité avec dir si c'est le cas
                            new_cycle._color = Grafik._colors[len(self._cycles) % len(Grafik._colors)]
                            self._cycles.append( new_cycle )
                                
    # ------------------------------------------------------------ detect_corner
    def detect_corners( self ):
        """
        Cherche tous les coins
        :Returns
        - corner : [Cell] liste de tous les coins.
        """
        corners = []
        for x in range(self._size):
            for y in range(self._size):
                # Pas forbid
                cell = self.get_cell((x,y))
                if cell._type != 'forbid':
                    cell._type = 'void'
                    # nb de mur
                    nb_ver = 0
                    nb_hor = 0
                    if x == 0 or x in self._ver_wall[y] or self.get_cell((x-1,y)).has_rob():
                        nb_ver += 1
                    if x == (self._size-1) or (x+1) in self._ver_wall[y] or self.get_cell((x+1,y)).has_rob():
                        nb_ver += 1
                    if y == 0 or y in self._hor_wall[x] or self.get_cell((x,y-1)).has_rob():
                        nb_hor += 1
                    if y == (self._size-1) or (y+1) in self._hor_wall[x] or self.get_cell((x,y+1)).has_rob():
                        nb_hor += 1
                    # debug
                    print "Cell : ",cell._pos," => V=",nb_ver," H=",nb_hor
                    if nb_ver == 1 and nb_hor == 1:
                        cell._type = 'corner'
                        corners.append( cell )
        return corners
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def get_cycle(self, pos):
        """
        Récupère le(s) cycle ou []
        :Param
        - pos : (x,y) position d'une Cell
        :Returns
        - [Cycle._labels]
        """
        cycle_names = []
        # la cell
        cell = self.get_cell( pos )
        # tous les tags qui commencent par 'c'
        for tag in cell._values.keys():
            if tag.startswith( 'c' ):
                cycle_names.append( tag )
        return cycle_names
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def clean_cycles(self, ):
        """Nettoie tous les cycles
        """
        for c in self._cycles:
            self.clean_cells_of_tag( c._label )
        self._cycles = []

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def get_cell( self, pos ):
        """La Cell à la position
        :Param
        - pos (x,y) : position dans la Board
        :Returns
        - Cell : cell à la position 'pos'
        """
        return self._cells[pos]
    # --------------------------------------------------------------- dump_cells
    def dump_cells( self ):
        """
        Affiche toutes les Cell actuelles.
        """
        for p,c in self._cells.iteritems():
            print p," -> ",c
    # ------------------------------------------------------- clean_cells_of_tag
    def clean_cells_of_tag( self, tag ):
        """
        Enlève la valeur associée à 'tag' pour toutes les Cell.
        :Param
        - tag (str)
        """
        for p,c in self._cells.iteritems():
            c.clean_of_tag( tag )
            
# ******************************************************************************
# ************************************************************************ Cycle
# ******************************************************************************
class Cycle:
    """
    Un Cycle va d'une bifurcation à une bifurcation, en ne passant que par des coins.
    Constitué par des _points, dont les extrémités (et des _arcs pour l'affichage)

    # >> bb.detect_corners()
    # >> c = Cycle(bb, "c1")
    # >> c.build_from_corner( (4,0), 3)
    # >> bb._cycles.append( t )
    # >> bb.draw_queue()
    """

    # --------------------------------------------------------------------- init
    def __init__(self, bb, label = "cycle"):
        """
        :Param
        - bb Board
        """
        self._bb = bb
        self._label = label
        self._depth_max = 1
        self._points = []
        self._ext = []
        self._arcs = []
        self._color = (0,1,0)
    # ---------------------------------------------------------------------- str
    def __str__(self):
        """
        Représentation comme str d'un Cycle
        """
        cyc_str = "CYCLE_"+self._label+"\n"
        for pt in self._points:
            cyc_str += "   "+self._bb.get_cell(pt).__str__()+"\n"
        return cyc_str
    # --------------------------------------------------------------------- draw
    def draw( self, cr):
        """
        Dessine la suite des arcs
        :Param
        - cr Cairo Context
        """
        # couleur et épaisseur
        cr.set_source_rgb( *self._color )
        cr.set_line_width(0.1)
        for arc in self._arcs:
            # segments
            cr.move_to( *arc[0] )
            cr.line_to( *arc[1] )
        cr.stroke()
        # extremités
        for ext in self._ext:
            # cr.arc( ext._pos[0], ext._pos[1], 0.05, 0, math.pi*2 )
            cr.move_to( ext._pos[0], ext._pos[1]+0.1 )
            cr.line_to( ext._pos[0]+0.1, ext._pos[1])
            cr.line_to( ext._pos[0], ext._pos[1]-0.1)
            cr.line_to( ext._pos[0]-0.1, ext._pos[1])
            cr.line_to( ext._pos[0], ext._pos[1]+0.1)
            cr.stroke()

    # -------------------------------------------------------------------- clean
    def clean( self ):
        """
        Faut nettoyer self._arcs mais aussi les valeurs des Cells de Board.
        """
        self._arcs = []
        self._points = []
        self._ext = []
        self._bb.clean_cells_of_tag( self._label )

    # -------------------------------------------------------- build_from_corner
    def build_from_corner(self, pos, depth_max=5):
        """
        Construit à partir d'un point qui DOIT être un 'corner'.
        :Param
        - pos : (x,y) pt de départ, doit être un corner.
        - depth_max : profonder maximum pour recherche un cycle (= longueur)
        """
        # TODO : vérifier que n'est pas déjà sur un cycle !
        self._depth_max = depth_max
        self.clean()
        
        self._points = [pos]
        self.expand( pos, None )
    # --------------------------------------------------------------------- todo
    def build_perpendicular_to(self, pos, dir):
        """
        Construit à partir d'un point qui est une extrémité sans suite.
        i.e, qui ne débouche sur rien.
        Return :
        - paires (pos, dir) si les extrémités sont a étendre aussi
        - None si le Cycle est nul
        Arguments:
        - `pos`: (x,y) pt de départ
        - `dir`: direction perpendiculaire à la direction de recherche
        """
        to_extend = []
        # Normalement, les deux extrémités qu'on va construire ne sont ni
        # des coins, ni le point de départ de la recherche.
        # Par contre, ces nouvelles extrémités peuvent de nouveaux être
        # des points de départ de 'build_perpendicular_to()'
        if dir == 'Up' or dir == 'Down':
            pos1 = self._bb._go['Left']( *pos )
            pos2 = self._bb._go['Right']( *pos )
            print "Extension de ",pos1," à ",pos2
            if pos1 == pos2 :
                return None
            # nouvel arc
            self._arcs.append( (pos1, pos2) )
            # maj des Cell de l'arc
            # start
            pos_cell = (pos1[0],pos1[1])
            cell = self._bb.get_cell( pos_cell )
            cell.append_to_tag( self._label, 'Right' )
            self._ext.append( cell )
            self._points.append( pos1 )
            # Tester s'il faut étendre les extrémités
            # Nombre de tag qui commencent par "c"
            l_tag = []
            for tag in cell._values.keys():
                    if tag.startswith('c'):
                        l_tag.append( tag )
            # Devrait y avoir 2 cycles.
            if len(l_tag) == 1:
                print pos1," a étendre"
                to_extend.append( (pos1, 'Left') )
            # middle
            for x in range( pos1[0]+1, pos2[0]) :
                pos_cell = (x,pos1[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Right' )
                cell.append_to_tag( self._label, 'Left' )
            # end
            pos_cell = (pos2[0],pos1[1])
            cell = self._bb.get_cell( pos_cell )
            cell.append_to_tag( self._label, 'Left')
            self._ext.append( cell )
            self._points.append( pos2 )
            # Tester s'il faut étendre les extrémités
            # Nombre de tag qui commencent par "c"
            l_tag = []
            for tag in cell._values.keys():
                    if tag.startswith('c'):
                        l_tag.append( tag )
            # Devrait y avoir 2 cycles.
            if len(l_tag) == 1:
                print pos2," a étendre"
                to_extend.append( (pos2, 'Right') )
        elif dir == 'Right' or dir == 'Left':
            pos1 = self._bb._go['Down']( *pos )
            pos2 = self._bb._go['Up']( *pos )
            print "Extension de ",pos1," à ",pos2
            if pos1 == pos2 :
                return None
            # nouvel arc
            self._arcs.append( (pos1, pos2) )
            # maj des Cell de l'arc
            # start
            pos_cell = (pos1[0],pos1[1])
            cell = self._bb.get_cell( pos_cell )
            cell.append_to_tag( self._label, 'Up' )
            self._ext.append( cell )
            self._points.append( pos1 )
            # Tester s'il faut étendre les extrémités
            # Nombre de tag qui commencent par "c"
            l_tag = []
            for tag in cell._values.keys():
                    if tag.startswith('c'):
                        l_tag.append( tag )
            # Devrait y avoir 2 cycles.
            if len(l_tag) == 1:
                print pos1," a étendre"
                to_extend.append( (pos1, 'Down') )
            # middle
            for x in range( pos1[0]+1, pos2[0]) :
                pos_cell = (x,pos1[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Up' )
                cell.append_to_tag( self._label, 'Down' )
            # end
            pos_cell = (pos2[0],pos1[1])
            cell = self._bb.get_cell( pos_cell )
            cell.append_to_tag( self._label, 'Down')
            self._ext.append( cell )
            self._points.append( pos2 )
            # Tester s'il faut étendre les extrémités
            # Nombre de tag qui commencent par "c"
            l_tag = []
            for tag in cell._values.keys():
                    if tag.startswith('c'):
                        l_tag.append( tag )
            # Devrait y avoir 2 cycles.
            if len(l_tag) == 1:
                print pos2," a étendre"
                to_extend.append( (pos2, 'Up') )

        return to_extend
    # ------------------------------------------------------------------- expand
    def expand( self, pos, dir_ori, depth=0 ):
        """
        Parcourt les directions dans le sens des aiguilles d'une montre, en profondeur d'abord.
        :Param
        - pos position actuelle
        - dir_ori : direction qu'on vient de prendre
        """
        # tab
        tab = "--"*depth
        # arrêt
        if depth > self._depth_max:
            return None
        # doit être un coin
        cell = self._bb.get_cell( pos )
        if cell._type != 'corner':
            print tab," ",pos," n'est pas un corner"
            self._ext.append( cell )
            return
        # Vers la droite
        if dir_ori != 'Left':
            print tab,"-> droite"
            possible = self._bb._go['Right']( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Right' )
                # middle
                for x in range( pos[0]+1, possible[0]) :
                    pos_cell = (x,pos[1])
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, 'Right' )
                    cell.append_to_tag( self._label, 'Left' )
                # end
                pos_cell = (possible[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Left' )
                # On continue ?
                if possible in self._points :
                    # # c'est aussi une extrémité
                    # self._ext.append( cell )
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, 'Right', depth+1)
        # Vers le bas
        if dir_ori != 'Up' :
            print tab,"-> bas"
            possible = self._bb._go['Down']( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Down' )
                # middle
                for y in range( possible[1]+1, pos[1]) :
                    pos_cell = (pos[0],y)
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, 'Down' )
                    cell.append_to_tag( self._label, 'Up' )
                # end
                pos_cell = (pos[0],possible[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Up' )
                # On continue ?
                if possible in self._points :
                    # # c'est aussi une extrémité
                    # self._ext.append( cell )
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, 'Down', depth+1)
        # Vers la gauche
        if dir_ori != 'Right' :
            print tab,"-> gauche"
            possible = self._bb._go['Left']( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Left' )
                # middle
                for x in range( possible[0]+1, pos[0]) :
                    pos_cell = (x,pos[1])
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, 'Right' )
                    cell.append_to_tag( self._label, 'Left' )
                # end
                pos_cell = (possible[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Right' )
                # On continue ?
                if possible in self._points :
                    # # c'est aussi une extrémité
                    # self._ext.append( cell )
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, 'Left', depth+1)
        # Vers le haut
        if dir_ori != 'Down' :
            print tab,"-> haut"
            possible = self._bb._go['Up']( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Up' )
                # middle
                for y in range( pos[1]+1, possible[1]) :
                    pos_cell = (pos[0],y)
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, 'Down' )
                    cell.append_to_tag( self._label, 'Up')
                # end
                pos_cell = (pos[0],possible[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, 'Down' )
                # On continue ?
                if possible in self._points :
                    # # c'est aussi une extrémité
                    # self._ext.append( cell )
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, 'Up', depth+1)
            # Rien d'autre à essayer
            print tab," Rien d'autre à essayer"
    def on_cycle(self, pos):
        """
        :Return
        - (False, None, None) si n'est pas sur le cycle
        - (True, 0, None) si c'est le premier point
        - (True, indice_avant, indice_après) sinon
        """
        print "is ",pos," on_cycle ",self.points
        if len(self.points) < 1:
            return (False, None, None)
        elif len(self.points) == 1:
            return (pos == self.points[0], 0, None)
        else:
            for ind in range(len(self.points)-1):
                p_ori = self.points[ind]
                p_next = self.points[ind+1]
                if pos[0] == p_ori[0] and pos[0] == p_next[0]:
                    if (p_ori[1] <= pos[1] and pos[1] <= p_next[1] ) or (p_ori[1] >= pos[1] and pos[1] >= p_next[1] ):
                        return (True, ind, ind+1 )
                elif pos[1] == p_ori[1] and pos[1] == p_next[1]:
                    if (p_ori[0] <= pos[0] and pos[0] <= p_next[0] ) or (p_ori[0] >= pos[0] and pos[0] >= p_next[0] ):
                        return (True, ind, ind+1)
        return (False, None, None)


# ******************************************************************************
# ************************************************************************* TODO
# ******************************************************************************

# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def affiche(widget):
    window = gtk.Window()
    window.resize(300,300)
    window.connect("delete-event", gtk.main_quit)
    window.add(widget)
    widget.show()
    window.present()
    gtk.main()
    print "affiche - end"

# *************************************************************** create_board16
def create_board16():
    """
    Crée une Board du jeu, de 16 x 16
    : Return
    - Board
    """
    # 0,0 est en bas à gauche.
    # Pour chaque ligne, la position des murs verticaux
    # [2,9,13] signifie à gauche des cases .,2, .,9 et .,13.
    ver_wall = [ [2,9,13],
                  [2,9],
                  [],
                  [],
                  [1,11,13],
                  [5,6,12],
                  [],
                  [7,9],
                  [7,9],
                  [],
                  [6,14],
                  [],
                  [5],
                  [5,14],
                  [12,14],
                  [6,9]]
    # 0,0 est en bas à gauche.
    # Pour chaque colonne, la position des murs horizontaux
    # [2,14] signifie en bas des cases 2,. et 14,.
    hor_wall = [ [2,14],
                  [4],
                  [2],
                  [],
                  [6,12],
                  [5,11,13],
                  [11],
                  [7,9],
                  [7,9],
                  [2],
                  [4],
                  [6,15],
                  [],
                  [4,13],
                  [10,15],
                  [4,12]]
    board = Board(16, ver_wall, hor_wall)
    # Case au centre sont interdites
    c = board.get_cell( (7,7) )
    c._type = 'forbid'
    c = board.get_cell( (7,8) )
    c._type = 'forbid'
    c = board.get_cell( (8,7) )
    c._type = 'forbid'
    c = board.get_cell( (8,8) )
    c._type = 'forbid'
    return board
# **************************************************************** create_board5
def create_board5():
    """
    Crée une Board du jeu, de 5 x 5
    : Return
    - Board
    """
    # 0,0 est en bas à gauche.
    # Pour chaque ligne, la position des murs verticaux
    # [2,9,13] signifie à gauche des cases .,2, .,9 et .,13.
    ver_wall = [ [2],
                  [],
                  [2,3],
                  [4],
                  []]
    # 0,0 est en bas à gauche.
    # Pour chaque colonne, la position des murs horizontaux
    # [2,14] signifie en bas des cases 2,. et 14,.
    hor_wall = [ [3],
                  [],
                  [2,3],
                  [4],
                  [2]]
    board = Board(5, ver_wall, hor_wall )
    # Case au centre est interdite
    c = board.get_cell( (2,2) )
    c._type = 'forbid'
    return board

# ******************************************************************************
# ************************************************************************* MAIN
# ******************************************************************************
if __name__ == "__main__":
    # bb = create_board5()
    bb = create_board16()
    #
    rr = Robot( bb )
    rr.put( (3,1) )
    bb._robot.append( rr )
    # bb.detect_corners()
    # bb.dump_cells()
    bb.build_basic_cycles()
    affiche(bb)
    
