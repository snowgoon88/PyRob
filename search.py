#!/usr/bin/python
# -*- coding: utf-8 -*-

# ******************************************************************************
# ******************************************************************** BraodTree
# ******************************************************************************
class BroadTree:
    """
    Recherche en largeur d'abord.
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
    def __init__( self, board, label="broad" ):
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

        # Pour la recherche incrémentale "manuelle"
        self._depth = 0
        self._cell_to_expand = []

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
    # --------------------------------------------------------------- build_step
    def build_step(self, pos ):
        """Construit l'arbre de manière incrémentale, en largeur.
        => self.expand_step
        :Param
        - `pos`: (x,y) position de départ
        """
        self._cell_to_expand = [ (None, pos) ]
        self._depth = 0
    # -------------------------------------------------------------- expand_step
    def expand_step(self, ):
        """Une étape de recherche en largeur.
        """
        if self._cell_to_expand <> []:
            # les cell à visiter au niveau prochain
            next_cells = []
            while( self._cell_to_expand <> [] ):
                c = self._cell_to_expand.pop()
                # ajoutes les éventuelles cell suivantes
                next_cells.extend( self.expand( c[0], c[1], None, self._depth ) )
            self._cell_to_expand = next_cells
            self._depth += 1
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
class DepthTree(object):
    """Recherche en profondeur d'abord
    """
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def __init__(self, board, label="depth"):
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

        # Pour la recherche incrémentale "manuelle"
        self._depth = 0
        self._path = []
        self._path_ind = 0
        self._next_dir = {'Right':'Down', 'Down':'Left',
                         'Left':'Up', 'Up':None}

        # pour dessiner
        self._arcs = []
        self._color = (1,0,0)
        # qu'est-ce qu'on dessine.
        self._draw_value = False
        self._draw_arc = True
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
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
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def clean( self ):
        """
        Faut nettoyer self._arcs mais aussi les valeurs des Cells de Board.
        """
        self._arcs = []
        self._path = []
        self._path_ind = 0
        self._bb.clean_cells_of_tag( self._label )
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def build_step(self, pos):
        """Initialise la recherche incrémentale
        => self.expand_step()
        :Param
        - `pos`: (x,y) position de départ
        """
        self._path = [ ('Right', pos) ]
        self._path_ind = 0
        self._depth = 0
        self._bb.get_cell( pos)._values[self._label] = self._depth
        print "path=",self._path
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def expand_step(self, ):
        """Un pas de recherche incrémentale
        """
        # tab
        tab = "[{0}]".format(self._depth)
        # point à explorer
        dir,pos = self._path[self._path_ind]
        
        # dir = None : backtracking
        if dir == None:
            print tab," TODO Backtracking"
            return self.backtrack()
        else:
            # prochain point
            next_dir,next_pt = self.next_point( pos, dir )
            if next_dir == None:
                self._path[self._path_ind] = (None,pos)
                # il faut faire du backtracking
                print tab," TODO Backtracking"
                return self.backtrack()
            else:
                # nouveau point, faut mettre à jour
                self._path[self._path_ind] = (next_dir,pos)
                # ajout
                self._depth += 1
                self._bb.get_cell( next_pt )._values[self._label] = self._depth
                self._path.append( ('Right', next_pt) )
                self._path_ind = len(self._path)-1
                self._arcs.append( (pos,next_pt) )
                return True
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def next_point(self, pos, dir):
        """Trouve le prochain point ou None
        :Param
        - `pos`: (x,y) position de départ
        - `dir`: première direction de recherche
        :Returns:
        - dir,new_pos : si dir mène à new_pos qui est a explorer
        - None,pos : si pos ne mène plus à rien
        """
        # tab
        tab = "[{0}]".format(self._depth)
        print tab,"next_point depuis {0}".format(pos)
        while( dir != None ):
            possible = self._bb._go[dir]( *pos )
            # même point
            if possible == pos:
                print tab," {0} => même point".format(dir)
                dir = self._next_dir[dir]
            else:
                # another point
                poss_val = self._bb.get_cell( possible )._values    
                # déja exploré
                if poss_val.has_key( self._label ):
                    print tab, " {0} => {1} déjà exploré".format(dir,possible)
                    dir = self._next_dir[dir]
                # nouveau point
                else:
                    print tab," {0} => {1} NEW".format(dir,possible)
                    return dir,possible
        # tout essayé
        print tab," Tout essayé"
        return None,pos
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def backtrack(self, ):
        """Remonte dans _path pour trouver no None.
        :Returns
        - True si il reste a explorer
        - False si plus rien (remonté au début)
        """
        while( self._path_ind >= 0 ):
            self._path_ind -= 1
            dir,pos = self._path[self._path_ind]
            if dir != None:
                return True
        print "raté"
        return False
                
        


        


# ******************************************************************************
# ************************************************************************** END
# ******************************************************************************
