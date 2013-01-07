# -*- coding: utf-8 -*-

import pygtk
import gtk, gobject, cairo
import copy

class Board( gtk.DrawingArea):

    _ver_wall = [ [2,9,13],
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
    _hor_wall = [ [2,14],
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

    def __init__(self, size):
        gtk.DrawingArea.__init__(self)
        self._size = size
        self._cells = {}
        self._cycles = []
        self._tree = []
        self.idleWork = -1
        self.setIdle( True )

        #self.mtrx = cairo.Matrix(fx,0,0,fy,cx*(1-fx),cy*(fy-1))
        self.mtrx = cairo.Matrix(1,0,0,-1, 0, 0 )

        self.add_events( gtk.gdk.BUTTON_PRESS_MASK )
        self.connect("expose-event", self.draw_cbk )
        self.connect("button-press-event", self.click_cbk)

    def setIdle(self, flag):
        """ True pour dessiner en idle, False sinon.
        """
        if( flag ) :
            if( self.idleWork == -1) :
                self.idleWork = gobject.idle_add( self.idle_callback )
        else :
            if( self.idleWork != -1) :
                gobject.source_remove( self.idleWork )
                self.idleWork = -1


    def draw_board( self, cr ):
        """
        :Param
        - cr Cairo Context
        """
        # Devrait choisir l'épaisseur et la couleur
        cr.set_source_rgb( 0, 0, 0)
        cr.set_line_width(0.02)
        for pos in range(self._size+1):
            cr.move_to( -0.5, pos-0.5 )
            cr.line_to( self._size-0.5, pos-0.5 )
            cr.move_to( pos-0.5, -0.5 )
            cr.line_to( pos-0.5, self._size-0.5 )
        cr.stroke()
        cr.set_line_width(0.1)
        cr.move_to( -0.5, -0.5 )
        cr.rel_line_to( self._size, 0 )
        cr.rel_line_to( 0, self._size )
        cr.rel_line_to( -self._size, 0)
        cr.rel_line_to( 0, -self._size )
        cr.stroke()

    def draw_walls(self, cr):
        # Devrait choisir l'épaisseur et la couleur
        cr.set_source_rgb( 0, 0, 0)
        cr.set_line_width(0.1)
        # Hor and vert
        for i in range(len(self._hor_wall)):
            for x in self._ver_wall[i]:
                cr.move_to( x-0.5, i-0.5)
                cr.rel_line_to( 0, 1)
                cr.stroke()
            for y in self._hor_wall[i]:
                cr.move_to( i-0.5, y-0.5)
                cr.rel_line_to( 1, 0)
                cr.stroke()

    def draw_axes(self, cr):
        """ Draw axes in Grey.
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

    def draw_value( self, cr, txt, pos_x, pos_y):
        cr.set_font_size(0.4)
        x_bearing, y_bearing, width, height = cr.text_extents( txt )[:4]
        cr.move_to(pos_x - width / 2 - x_bearing, pos_y - height / 2 - y_bearing)
        cr.save()
        cr.transform( self.mtrx )
        cr.show_text(txt)
        cr.restore()
    def draw_cycles(self, cr):
        for cy in self._cycles:
            cy.draw( cr )
    def draw_tree(self, cr):
        for t in self._tree:
            t.draw( cr )
    def draw(self, cr, width, height):
        # Fill the background with white
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        # set up a transform so that board
        # maps to (0,0)x(width, height)
        cr.scale(width / (self._size + 2.0),
                 -height / (self._size + 2.0) )
        cr.translate( 1.0 , -self._size-1.0 )
        # draw
        self.draw_axes(cr)
        self.draw_board(cr)
        self.draw_walls(cr)
        self.draw_cycles(cr)
        self.draw_tree(cr)

    def draw_cbk( self, widget, event ):
        # Create the cairo context
        cr = self.window.cairo_create()
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y,
                event.area.width, event.area.height)
        cr.clip()
        #
        self.draw(cr, *self.window.get_size())
        return True

    def click_cbk( self, widget, event ):
        width,height = self.window.get_size()
        print event," x=",event.x," (",event.x*(self._size+2.0)/width-0.5,") y=",event.y," (",(height-event.y)*(self._size+2.0)/height-0.5,")"

    # IdleCallback
    def idle_callback(self):
        #print "Idle"
        # Create the cairo context
        cr = self.window.cairo_create()

        self.draw(cr, *self.window.get_size())
        return True


    def go_right( self, pos_x, pos_y ):
        walls = self._ver_wall[pos_y]
        pos = min([p for p in walls if p>pos_x]+[16])
        return (pos-1,pos_y)
    def go_left( self, pos_x, pos_y ):
        walls = self._ver_wall[pos_y]
        pos = max([p for p in walls if p<=pos_x]+[0])
        return (pos,pos_y)
    def go_up( self, pos_x, pos_y ):
        walls = self._hor_wall[pos_x]
        pos = min([p for p in walls if p>pos_y]+[16])
        return (pos_x,pos-1)
    def go_down( self, pos_x, pos_y ):
        walls = self._hor_wall[pos_x]
        pos = max([p for p in walls if p<=pos_y]+[0])
        return (pos_x,pos)
    def delta_up( self, pos_x, pos_y ):
        wall_x,wall_y = self.go_down( pos_x, pos_y)
        return pos_y - wall_y
    def delta_down( self, pos_x, pos_y ):
        wall_x,wall_y = self.go_up( pos_x, pos_y)
        return wall_y - pos_y
    def delta_left( self, pos_x, pos_y ):
        wall_x,wall_y = self.go_right( pos_x, pos_y)
        return wall_x - pos_x
    def delta_right( self, pos_x, pos_y ):
        wall_x,wall_y = self.go_left( pos_x, pos_y)
        return pos_x - wall_x
    def get_cell( self, pos ):
        if self._cells.has_key( pos ):
            return self._cells[pos]
        else:
            return None
    def dump_cells( self ):
        for p,c in self._cells.iteritems():
            print p," -> ",c
    def clean_cells_of_tag( self, tag ):
        for p,c in self._cells.iteritems():
            c.clean_of_tag( tag )
            
class Cycle:
    def __init__(self, bb):
        """
        :Param
        - bb Board
        """
        self._bb = bb
        self._depth_max = 1
        self.points = []
        self.color = (0,0,1)

    def clone(self):
        other = Cycle( self._bb)
        other._depth_max = self._depth_max
        other.points = copy.deepcopy( self.points )
        other.color = self.color
        return other

    def draw( self, cr):
        #print "Drawing ",self.points
        if len(self.points) > 1:
            # Devrait choisir l'épaisseur et la couleur
            cr.set_source_rgb( *self.color )
            cr.set_line_width(0.1)
            # lines
            cr.move_to( *self.points[0] )
            for pt in self.points:
                cr.line_to( *pt )
            cr.stroke()

    def make_default(self):
        self.points = [ (0,0), (0,1), (1,1), (1, 5)]

    def build_from(self, pos, depth_max=5):
        self._depth_max = depth_max
        self.points = [pos]
        self.expand( pos, None )
        

    def expand( self, pos, dir_ori, depth=0 ):
        """
        :Param
        - pos position actuelle
        - dir_ori : direction qu'on vient de prendre
        """
        # tab
        tab = "--"*depth
        # arrêt
        if depth > self._depth_max:
            return None
        # essaie right
        if dir_ori <> self._bb.go_right and dir_ori<> self._bb.go_left:
            finish = self._bb.go_right( *pos )
            if finish <> pos:
                print tab,"Right OK ",finish
                # sur le cycle => on ferme
                keep = self.on_cycle( finish )
                if keep[0] == True:
                    self.close( finish, keep[2] )
                else:
                    other = self.clone()
                    other.points.append( finish )
                    other.expand( finish, self._bb.go_right, depth+1)
        # essaie left
        if dir_ori <> self._bb.go_left and dir_ori<> self._bb.go_right:
            finish = self._bb.go_left( *pos )
            if finish <> pos:
                print tab,"Left OK ",finish
                # sur le cycle => on ferme
                keep = self.on_cycle( finish )
                if keep[0] == True:
                    self.close( finish, keep[2] )
                else:
                    other = self.clone()
                    other.points.append( finish )
                    other.expand( finish, self._bb.go_left, depth+1)
        # essaie up
        if dir_ori <> self._bb.go_up and dir_ori<> self._bb.go_down:
            finish = self._bb.go_up( *pos )
            if finish <> pos:
                print tab,"Up OK ",finish
                # sur le cycle => on ferme
                keep = self.on_cycle( finish )
                if keep[0] == True:
                    self.close( finish, keep[2] )
                else:
                    other = self.clone()
                    other.points.append( finish )
                    other.expand( finish, self._bb.go_up, depth+1)
        # essaie down
        if dir_ori <> self._bb.go_down and dir_ori<> self._bb.go_up:
            finish = self._bb.go_down( *pos )
            if finish <> pos:
                print tab,"Down OK ",finish
                # sur le cycle => on ferme
                keep = self.on_cycle( finish )
                if keep[0] == True:
                    self.close( finish, keep[2] )
                else:
                    other = self.clone()
                    other.points.append( finish )
                    other.expand( finish, self._bb.go_down, depth+1)

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

    def close(self, pt, indice):
        print "Fermeture de ",self.points
        print "   --> en ", pt, " avant ", indice
        print "   --> ",[pt] + self.points[indice:]+[pt]
        return [pt]+self.points[indice:]+[pt]

class ReachTree:
    # ------------------------------------------------------------------------------
    def __init__( self, board, label="reach" ):
        # un label
        self._label = label
        # un board
        self._bb = board
        # pour dessiner
        self._arcs = []
        self._color = (0,0,1)
        self._draw_value = False
        self._draw_arc = True
    # ------------------------------------------------------------------------------
    def draw( self, cr):
        # couleur et épaisseur
        cr.set_source_rgb( *self._color )
        cr.set_line_width(0.1)
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
    # ------------------------------------------------------------------------------
    def clean( self ):
        self._arcs = []
    # ------------------------------------------------------------------------------
    def build( self, pos, depth_max=5):
        """
        Construit l'arbre en utilisant une recherche en largeur.
        """
        # initialise les cell à visiter
        cell_to_expand = [ (None, pos) ]
        depth = 0
        # tant qu'il en reste à visiter
        print "A visiter: ",cell_to_expand
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
    # ------------------------------------------------------------------------------
    def expand( self, prev_pos, pos, prev_dir, depth=0):
        """
        Ajoute des arcs et des valeurs aux cases.
        Renvoie une liste de prochains points à parcourir ou None.
        """
        # tab
        tab = "--"*depth
        # cell est la case courante
        cell = self._bb.get_cell( pos)
        if cell is None:
            cell = Cell( pos )
            self._bb._cells[ pos ] = cell
        #si case courante n'a pas de valeur attachée à cet arbre
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

class ToTree:
    # ------------------------------------------------------------------------------
    def __init__( self, board, label="to" ):
        # un label
        self._label = label
        # un board
        self._bb = board
        # pour dessiner
        self._arcs = []
        self._color = (2,0,0)
        self._draw_value = False
        self._draw_arc = True
    # ------------------------------------------------------------------------------
    def draw( self, cr):
        # couleur et épaisseur
        cr.set_source_rgb( *self._color )
        cr.set_line_width(0.1)
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
                    self._bb.draw_value( cr, str(c._values[self._label]), p[0]-0.3, p[1])
    # ------------------------------------------------------------------------------
    def clean( self ):
        self._arcs = []
        self._bb.clean_cells_of_tag( self._label )
    # ------------------------------------------------------------------------------
    def build( self, pos, depth_max=5, delta_max=0 ):
        """
        Construit l'arbre en utilisant une recherche en largeur.
        """
        # initialise les cell à visiter (prev_pos, act_pos, prev_dir, depth)
        cell_to_expand = [ (None, pos, None, 0) ]
        depth = 0
        # tant qu'il en reste à visiter
        print "A visiter: ",cell_to_expand
        while( cell_to_expand <> [] and depth < depth_max ):
            # les cell à visiter au niveau prochain
            next_cells = []
            while( cell_to_expand <> [] ):
                print "Poping from ",cell_to_expand
                c = cell_to_expand.pop()
                # ajoutes les éventuelles cell suivantes
                next_cells.extend( self.expand( c[0], c[1], c[2], c[3], delta_max ) )
            cell_to_expand = next_cells
            depth += 1
    # ------------------------------------------------------------------------------
    def expand( self, prev_pos, pos, prev_dir, depth=0, max_delta=0):
        """
        Ajoute des arcs et des valeurs aux cases.
        Renvoie une liste de prochains points à parcourir ou None.
        """
        # tab
        tab = "--"*depth
        # cell est la case courante
        cell = self._bb.get_cell( pos)
        if cell is None:
            cell = Cell( pos )
            self._bb._cells[ pos ] = cell
        #si case courante n'a pas de valeur attachée à cet arbre
        if( cell._values.has_key( self._label ) is False or (cell._values[self._label] >= depth )):
            print tab,"case actuelle = ", pos, " depth=",depth
            # longueur actuelle du trajet
            cell._values[self._label] = depth
            # nouvel arc
            if( prev_pos is not None):
                self._arcs.append( (prev_pos,pos) )
            # liste des cases qu'on peut atteindre
            cell_suivantes = []
            pos_x,pos_y = pos
            # vers le haut si vient pas du bas
            if prev_dir <> self._bb.go_down:
                print tab,"not coming from Down"
                delta = self._bb.delta_up( *pos )
                print tab,"delta =",delta
                if delta < max_delta:
                    possible = self._bb.go_up( *pos )
                    if possible <> pos:
                        print tab,"Up possible ",possible
                        fin_x,fin_y = possible
                        for tmp_y in range( pos_y+1, fin_y+1 ):
                            print tab,"testing ",pos_x," ",tmp_y
                            if (self._bb.delta_right( pos_x, tmp_y ) < max_delta) or (self._bb.delta_left( pos_x, tmp_y) < max_delta):
                                print tab,"added"
                                cell_suivantes.append( (pos, (pos_x,tmp_y), self._bb.go_up, depth+delta+1) )
            # vers la droite si vient pas de la gauche
            if prev_dir <> self._bb.go_left:
                print tab,"not coming from Left"
                delta = self._bb.delta_right( *pos )
                print tab,"delta =",delta
                if delta < max_delta:
                    possible = self._bb.go_right( *pos )
                    if possible <> pos:
                        print tab,"Right possible ",possible
                        fin_x,fin_y = possible
                        for tmp_x in range( pos_x+1, fin_x+1 ):
                            print tab,"testing ",tmp_x," ",pos_y
                            if (self._bb.delta_up( tmp_x, pos_y ) < max_delta) or (self._bb.delta_down( tmp_x, pos_y) < max_delta):
                                print tab,"added"
                                cell_suivantes.append( (pos, (tmp_x,pos_y), self._bb.go_right, depth+delta+1) )
            # vers le bas si vient pas du haut
            if prev_dir <> self._bb.go_up:
                print tab,"not coming from Up"
                delta = self._bb.delta_down( *pos )
                print tab,"delta =",delta
                if delta < max_delta:
                    possible = self._bb.go_down( *pos )
                    if possible <> pos:
                        print tab,"Down possible ",possible
                        fin_x,fin_y = possible
                        for tmp_y in range( fin_y, pos_y ):
                            print tab,"testing ",pos_x," ",tmp_y
                            if (self._bb.delta_right( pos_x, tmp_y ) < max_delta) or (self._bb.delta_left( pos_x, tmp_y) < max_delta):
                                print tab,"added"
                                cell_suivantes.append( (pos, (pos_x,tmp_y), self._bb.go_down, depth+delta+1) )
            # vers la gauche si vient pas de la droite
            if prev_dir <> self._bb.go_right:
                print tab,"not coming from Right"
                delta = self._bb.delta_left( *pos )
                print tab,"delta =",delta
                if delta < max_delta:
                    possible = self._bb.go_left( *pos )
                    if possible <> pos:
                        print tab,"Left possible ",possible
                        fin_x,fin_y = possible
                        for tmp_x in range( fin_x, pos_x ):
                            print tab,"testing ",tmp_x," ",pos_y
                            if (self._bb.delta_up( tmp_x, pos_y ) < max_delta) or (self._bb.delta_down( tmp_x, pos_y) < max_delta):
                                print tab,"added"
                                cell_suivantes.append( (pos, (tmp_x,pos_y), self._bb.go_left, depth+delta+1) )
            return cell_suivantes
        # si elle a déjà une valeur, on va dire qu'elle est inférieure donc on 
        # s'arrête, mais rien n'est moins sûr
        else:
            return []
class Cell(object):
    # ------------------------------------------------------------------------------
    def __init__(self, pos):
        self._pos = pos
        self._type = 'vide'
        self._values = {}
    # ------------------------------------------------------------------------------
    def __str__(self):
        return self._pos.__str__()+" ["+self._type+"]\n"+"values="+self._values.__str__()
    # ------------------------------------------------------------------------------
    def clean_of_tag( self, tag ):
        if self._values.has_key( tag ):
            self._values.pop( tag )

def categorize_cells( bb ):
    corner = []
    biffur = []
    for x in range(bb._size):
        for y in range(bb._size):
            # nb de mur
            nb_ver = 0
            nb_hor = 0
            if x==0 or x in bb._ver_wall[y]:
                nb_ver += 1
            if x==15 or (x+1) in bb._ver_wall[y]:
                nb_ver += 1
            if y==0 or y in bb._hor_wall[x]:
                nb_hor += 1
            if y==15 or (y+1) in bb._hor_wall[x]:
                nb_hor += 1
            if nb_ver == 1 and nb_hor == 1:
               corner.append( (x,y) )
            elif (nb_ver == 1 and nb_hor == 0) or (nb_ver == 0 and nb_hor == 1):
                biffur.append( (x,y) )
    return corner,biffur
            
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def affiche(widget):
    window = gtk.Window()
    window.resize(300,300)
    window.connect("delete-event", gtk.main_quit)
    widget.show()
    window.add(widget)
    window.present()
    gtk.main()

if __name__ == "__main__":
    bb = Board(16)
    affiche(bb)
    #l = Cycle(bb)
    #ld = Cycle(bb)
    #ld.make_default()
    #
    #t = ReachTree( bb, "t1" )
    #t.clean()
    #t.build( (0,0), 16)
    #bb._tree.append( t )

    
