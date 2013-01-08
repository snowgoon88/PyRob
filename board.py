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
# >> t = ReachTree( bb, "t1" )
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
import robot
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
        Initialise la Board de taille size x size.
        No Cells, Cycles or Tree.
        :Param
        - size Taille d'un coté de la Board
        """
        gtk.DrawingArea.__init__(self)
        print "Board.__init__"

        self._size = size
        self._ver_wall = vert_wall
        self._hor_wall = hor_wall

        self._cells = {}
        self._cycles = []
        self._tree = []
        self._robot = []

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
        self.draw_cycles(cr)
        self.draw_trees(cr)
        self.draw_robots(cr)
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
    # ---------------------------------------------------------------- click_cbk
    def click_cbk( self, widget, event ):
        """
        Affiche 'event' et coordonnées de la souris.
        Callback de gtk.DrawingArea.
        """
        width,height = self.window.get_size()
        print event," x=",event.x," (",event.x*(self._size+2.0)/width-0.5,") y=",event.y," (",(height-event.y)*(self._size+2.0)/height-0.5,")"
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
        TODO ne tient compte que des murs !
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._ver_wall[pos_y]
        pos = min([p for p in walls if p>pos_x]+[self._size])
        return (pos-1,pos_y)
    # ------------------------------------------------------------------ go_left
    def go_left( self, pos_x, pos_y ):
        """
        TODO ne tient compte que des murs !
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._ver_wall[pos_y]
        pos = max([p for p in walls if p<=pos_x]+[0])
        return (pos,pos_y)
    # -------------------------------------------------------------------- go_up
    def go_up( self, pos_x, pos_y ):
        """
        TODO ne tient compte que des murs !
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._hor_wall[pos_x]
        pos = min([p for p in walls if p>pos_y]+[self._size])
        return (pos_x,pos-1)
    # ------------------------------------------------------------------ go_down
    def go_down( self, pos_x, pos_y ):
        """
        TODO ne tient compte que des murs !
        :Return
        - (x,y) atteint dans la direction à partir de (pos_x,pos_y)
        """
        walls = self._hor_wall[pos_x]
        pos = max([p for p in walls if p<=pos_y]+[0])
        return (pos_x,pos)


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
            if len(cn) == 0 :
                print " build cycle..."
                # Faire un nouveau cycle
                cyc = Cycle( self, 'c'+str(len(self._cycles)) )
                cyc.build_from_corner( coin._pos, 15 )
                cyc._color = Grafik._colors[len(self._cycles) % len(Grafik._colors)]
                self._cycles.append( cyc )
        print "Trouvé ",len(self._cycles)," cycles"
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
                # nb de mur
                nb_ver = 0
                nb_hor = 0
                if x == 0 or x in self._ver_wall[y]:
                    nb_ver += 1
                if x == (self._size-1) or (x+1) in self._ver_wall[y]:
                    nb_ver += 1
                if y == 0 or y in self._hor_wall[x]:
                    nb_hor += 1
                if y == (self._size-1) or (y+1) in self._hor_wall[x]:
                    nb_hor += 1
                if nb_ver == 1 and nb_hor == 1:
                    cell = self.get_cell( (x,y) )
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
    def get_cell( self, pos ):
        """
        Crée la Cell si elle n'existe pas.
        :Param
        - pos (x,y) : position dans la Board
        :Returns
        - Cell : cell à la position 'pos'
        """
        if self._cells.has_key( pos ):
            return self._cells[pos]
        else:
            cell = Cell( pos )
            self._cells[pos] = cell
            return cell
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


    # --------------------------------------------------------------------- draw
    def draw( self, cr):
        """
        Dessine la suite des arcs
        :Param
        - cr Cairo Context
        """
        # couleur et épaisseur
        cr.set_source_rgb( *self._color )
        cr.set_line_width(0.02)
        for arc in self._arcs:
            # segments
            cr.move_to( *arc[0] )
            cr.line_to( *arc[1] )
        cr.stroke()
        # extremités
        for ext in self._ext:
            cr.arc( ext._pos[0], ext._pos[1], 0.05, 0, math.pi*2 )
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
        if dir_ori != self._bb.go_left :
            print tab,"-> droite"
            possible = self._bb.go_right( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_right )
                # middle
                for x in range( pos[0]+1, possible[0]) :
                    pos_cell = (x,pos[1])
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, self._bb.go_right )
                    cell.append_to_tag( self._label, self._bb.go_left )
                # end
                pos_cell = (possible[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_left )
                # On continue ?
                if possible in self._points :
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, self._bb.go_right, depth+1)
        # Vers le bas
        if dir_ori != self._bb.go_up :
            print tab,"-> bas"
            possible = self._bb.go_down( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_down )
                # middle
                for y in range( possible[1]+1, pos[1]) :
                    pos_cell = (pos[0],y)
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, self._bb.go_down )
                    cell.append_to_tag( self._label, self._bb.go_up )
                # end
                pos_cell = (pos[0],possible[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_up )
                # On continue ?
                if possible in self._points :
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, self._bb.go_down, depth+1)
        # Vers la gauche
        if dir_ori != self._bb.go_right :
            print tab,"-> gauche"
            possible = self._bb.go_left( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_left )
                # middle
                for x in range( possible[0]+1, pos[0]) :
                    pos_cell = (x,pos[1])
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, self._bb.go_right )
                    cell.append_to_tag( self._label, self._bb.go_left )
                # end
                pos_cell = (possible[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_right )
                # On continue ?
                if possible in self._points :
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, self._bb.go_left, depth+1)
        # Vers le haut
        if dir_ori != self._bb.go_down :
            print tab,"-> haut"
            possible = self._bb.go_up( *pos )
            if possible <> pos :
                print tab,"ok de ",pos," à ",possible
                # nouvel arc
                self._arcs.append( (pos, possible) )
                # maj des Cell de l'arc
                # start
                pos_cell = (pos[0],pos[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_up )
                # middle
                for y in range( pos[1]+1, possible[1]) :
                    pos_cell = (pos[0],y)
                    cell = self._bb.get_cell( pos_cell )
                    cell.append_to_tag( self._label, self._bb.go_down )
                    cell.append_to_tag( self._label, self._bb.go_up )
                # end
                pos_cell = (pos[0],possible[1])
                cell = self._bb.get_cell( pos_cell )
                cell.append_to_tag( self._label, self._bb.go_down )
                # On continue ?
                if possible in self._points :
                    return
                else :
                    self._points.append( possible )
                    self.expand( possible, self._bb.go_up, depth+1)
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

class ReachTree:
    """
    Quels points (Cell) peuvent être atteint à partir d'une position de départ.
    Met à jour les Cell de Board (avec un tag = self._label), la valeur étant celle de la profondeur dans l'arbre.
    Constitué d'une collection d'arcs = (pos, pos).
    
    # >> t = ReachTree( bb, "t1" )
    # >> t._draw_arc = True
    # >> t._draw_value = True # aussi valeurs des cases
    # >> bb._tree.append( t )
    # >> t.clean()
    # >> t.build( (0,1), 6)
    # >> bb.draw_queue()    
    """
    # --------------------------------------------------------------------- init
    def __init__( self, board, label="reach" ):
        """
        Attaché à un Board, avec un label unique!
        :Param
        - board un Board
        - label (str) doit être unique
        """
        # un label
        self._label = label
        # un board
        self._bb = board
        # pour dessiner
        self._arcs = []
        self._color = (0,0,1)
        # qu'est-ce qu'on dessine.
        self._draw_value = False
        self._draw_arc = True

    # --------------------------------------------------------------------- draw
    def draw( self, cr):
        """
        Dessine la suite des arcs, et les valeurs des cases.
        :Param
        - cr Cairo Context
        """
        # couleur et épaisseur
        cr.set_source_rgb( *self._color )
        cr.set_line_width(0.01)
        if self._draw_arc:
            for arc in self._arcs:
                # segments
                cr.move_to( *arc[0] )
                cr.line_to( *arc[1] )
            cr.stroke()
        # aussi les cases ?
        if self._draw_value:
            for p,c in self._bb._cells.iteritems():
                if c._values.has_key( self._label):
                    self._bb.draw_value( cr, str(c._values[self._label]), p[0]+0.3, p[1]-0.5)

    # -------------------------------------------------------------------- clean
    def clean( self ):
        """
        Faut nettoyer self._arcs mais aussi les valeurs des Cells de Board.
        """
        self._arcs = []
        self._bb.clean_cells_of_tag( self._label )

    # -------------------------------------------------------------------- build
    def build( self, pos, depth_max=5):
        """
        Construit l'arbre en utilisant une recherche en largeur.
        => self.expand()
        :Param
        - pos (x,y) position de départ
        - depth_max profondeur maximum de recherche
        """
        # initialise les cell à visiter
        cell_to_expand = [ (None, pos) ]
        depth = 0
        # tant qu'il en reste à visiter
        print "cell_to_expand: ",cell_to_expand
        while( cell_to_expand <> [] and depth < depth_max ):
            # les cell à visiter au niveau prochain
            next_cells = []
            while( cell_to_expand <> [] ):
                print "Poping from ",cell_to_expand
                c = cell_to_expand.pop()
                # ajoutes les éventuelles cell suivantes
                next_cells.extend( self.expand( c[0], c[1], None, depth ) )
            cell_to_expand = next_cells
            depth += 1
    # ------------------------------------------------------------------- expand
    def expand( self, prev_pos, pos, prev_dir, depth=0):
        """
        Ajoute des arcs et des valeurs aux cases.
        Renvoie une liste de prochains points à parcourir ou None.
        :Param
        - prev_pos (x,y) ou None : position d'où on vient
        - pos (x,y) : position à étendre
        - prev_dir : TODO utile ???
        - depth : profondeur actuelle
        """
        # tab
        tab = "--"*depth
        # cell est la case courante
        cell = self._bb.get_cell( pos)
        print tab,"cell=",cell
        #si case courante n'a pas de valeur attachée à cet arbre
        # on crée un nouvel arc et, dans chaque direction, on ajoute une 
        # éventuelle nouvelle cell possible.
        if( cell._values.has_key( self._label ) is False or (cell._values[self._label] >= depth )):
            print tab,"case actuelle = ", pos, " depth=",depth
            # longueur actuelle du trajet
            cell._values[self._label] = depth
            # nouvel arc
            if( prev_pos is not None):
                self._arcs.append( (prev_pos,pos) )
            # liste des cases qu'on peut atteindre
            cell_suivantes = []
            # vers le haut
            possible = self._bb.go_up( *pos )
            if possible <> pos:
                print tab,"Up OK ",possible
                cell_suivantes.append( (pos, possible ) )
            # vers la droite
            possible = self._bb.go_right( *pos )
            if possible <> pos:
                print tab,"Right OK ",possible
                cell_suivantes.append( (pos, possible) )
            # vers le bas
            possible = self._bb.go_down( *pos )
            if possible <> pos:
                print tab,"Down OK ",possible
                cell_suivantes.append( (pos, possible) )
            # vers la gauche
            possible = self._bb.go_left( *pos )
            if possible <> pos:
                print tab,"Left OK ",possible
                cell_suivantes.append( (pos, possible) )
            return cell_suivantes
        #si case courante a déjà une valeur, elle est forcément inférieure => stop
        else:
            return []

# ******************************************************************************
# ************************************************************************* TODO
# ******************************************************************************

# ******************************************************************************
# ************************************************************************* Cell
# ******************************************************************************
class Cell(object):
    """
    Une Cell a:
    - une position (_pos=(x,y)),
    - un type (_type = 'vide',... )
    - un ensemble de valeurs attaché à des labels _values = { label:val }
    """

    # --------------------------------------------------------------------- init
    def __init__(self, pos):
        """
        Création comme une Cell 'vide' sans valeurs.
        :Param
        - pos (x,y)
        """
        self._pos = pos
        self._type = 'vide'
        self._values = {}

    # ---------------------------------------------------------------------- str
    def __str__(self):
        """
        Représentation comme str d'une Cell.
        """
        return self._pos.__str__()+" ["+self._type+"] "+"values="+self._values.__str__()

    # ------------------------------------------------------------- clean_of_tag
    def clean_of_tag( self, tag ):
        """
        Enlève la valeur associée au 'tag' donné
        :Param
        - tag (str)
        """
        if self._values.has_key( tag ):
            self._values.pop( tag )
    # ------------------------------------------------------------ append_to_tag
    def append_to_tag( self, tag, val):
        """
        Valeur de tag est une liste, ajoute ou crée.
        """
        if self._values.has_key( tag ) :
            self._values[tag].append( val )
        else:
            self._values[tag] = [val]
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
    return board

# ******************************************************************************
# ************************************************************************* MAIN
# ******************************************************************************
if __name__ == "__main__":
    bb = create_board5()
    #
    rr = robot.Robot( bb )
    rr.put( (3,1) )
    bb._robot.append( rr )
    # bb = create_board16()
    bb.build_basic_cycles()
    affiche(bb)

