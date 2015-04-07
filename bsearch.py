#!/usr/bin/python
# -*- coding: utf-8 -*-

from robot import *
import board as BO
import copy
import pygtk
import gtk, gobject, cairo

# ******************************************************************************
# *********************************************************************** State
# ******************************************************************************
class State(object):
    """ Etat light avec juste (label,pos) pour chaque robot, et un état précédent.
    """
    # ------------------------------------------------------------ __init__
    def __init__(self, l_robot=None, prev=None, rob=None, dir=None):
        """ Initialisation à partir d'une liste de robots
        
        Params:
        - `prev` : the previous state
        - `rob` : Robot moved
        - `dir` : direction of movement
        """
        self._prev = prev
        self._rob = rob
        self._dir = dir
        self._d_robot = {}
        if l_robot:
            for rob in l_robot:
                self._d_robot[rob._label] = rob._pos
    # ------------------------------------------------------------------- copy
    def copy(self, ):
        """ Fait une copie de self
        """
        other = State()
        for rob in self._d_robot:
            other._d_robot[rob] = self._d_robot[rob]
        return other
    # ---------------------------------------------------------------- is_same
    def is_same(self, other):
        """ Même valeur qu'un autre State
        
        Params:
        - `other`: un State
        """
        if len(other._d_robot) != len(self._d_robot):
            return False
        for lab in self._d_robot:
            if other._d_robot[lab] != self._d_robot[lab]:
                return False
        return True
    # --------------------------------------------------------------- dump_str
    def display_str(self, ):
        """
        """
        dump = "["
        for r,p in self._d_robot.iteritems():
            dump += "{0}:{1}; ".format( r, p )
        dump += "]"
        return dump
    # --------------------------------------------------------------- move_str
    def move_str(self, ):
        """ Affiche le mouvement amenant à ce State
        """
        move = ""
        if self._prev != None:
            move += self._rob._label+" to "+self._dir
        else:
            move += "None"
        return move
    
# ******************************************************************************
# ********************************************************************** SOLTREE
# ******************************************************************************
class SolTree(object):
    """ Arbre des mouvement pour la solution lors d'une recherche exaustive
    """
    
    def __init__(self, board, label="sol"):
        """ Attaché à un Board, avec un label unique
        
        :Param
        - `board`:
        - `label`:
        """
        self._board = board
        self._label = label

        # pour dessiner [ (col, pos_from, pos_to ) ]
        self._arcs = []
        
    # --------------------------------------------------------- build_from_sol
    def build_from_sol(self, l_state):
        """ Construits les différents arcs en fonction de la séquence de State
        et ajoute la profondeur comme valeur dans chaque case.
        
        Params:
        - `l_state`: séquence de State
        """
        for i in range(len(l_state)-1):
            src = l_state[i]
            dst = l_state[i+1]
            rob = dst._rob
            self._arcs.append( (rob._color,
                                src._d_robot[rob._label],
                                dst._d_robot[rob._label]) )
            # cell est la case dst
            cell = self._board.get_cell( dst._d_robot[rob._label] )
            cell._values[self._label] = (i+1)
    # ------------------------------------------------------------------- draw
    def draw(self, cr):
        """ Dessine la suite des arcs menant à la solution
        
        Params:
        - `cr`: Cairo Context
        """
        # Epaisseur
        cr.set_line_width( 0.01 )
        for arc in self._arcs:
            cr.set_source_rgb( *arc[0] )
            cr.move_to( *arc[1] )
            cr.line_to( *arc[2] )
        cr.stroke()

        # et aussi les valeurs stockées dans les cases
        for p,c in self._board._cells.iteritems():
                if c._values.has_key( self._label):
                    self._board.draw_value( cr, str(c._values[self._label]), p[0]+0.3, p[1]-0.5)

    # -------------------------------------------------------------------- clean
    def clean( self ):
        """
        Faut nettoyer self._arcs mais aussi les valeurs des Cells de Board.
        """
        self._arcs = []        

        

# ******************************************************************************
# ****************************************************************** BROADSEARCH
# ******************************************************************************
class BroadSearch(object):
    """ Recherche en largeur d'abord sur tous les robots
    """
    
    def __init__(self, board):
        """ Initialise avec les robots sur le board
        """
        self._bb = board
        self._depth = 0
        self._goal = None

        # add current state to state
        self._seen = []
        self._next = [State(board._robot)]
        self._explore = []

    # --------------------------------------------------------------- status_str
    def status_str(self, ):
        """
        """
        status = "Depth={0} : seen {1} states, {2} to explore".format( self._depth, len(self._seen), len(self._explore))
        return status
    # --------------------------------------------------------------- list_str
    def list_str(self, l_state):
        """ Affiche tous les State de la liste
        
        Params:
        - `l_state`: liste de State
        """
        str = "{"
        for s in l_state:
            str += s.display_str()+"; "
        str += "}"
        return str
    # ----------------------------------------------------------------- not_in
    def not_in(self, state, l_state):
        """ Est-ce que state et dans l_state (en terme de valeur, et non de
        référence.

        Params:
        - `state`: un State
        - `l_state`: une liste de State
        """
        for v in l_state:
            if state.is_same( v ):
                return False
        return True
    # --------------------------------------------------------- target_reached
    def target_reached(self, state):
        """ La cible est atteinte par le bon robot ?
        """
        for r in self._bb._target._l_rob:
            if state._d_robot[r._label] == self._bb._target._pos:
                print "State : " + state.display_str()
                print "Target : " + self._bb._target.display_str()
                return True
        return False
    # -------------------------------------------------------------- find_traj
    def find_traj(self, start_state):
        """ Remonte le long des states pour afficher la trajectoire
        """
        state = start_state
        traj = [state]
        while state._prev != None:
            state = state._prev
            traj.insert(0,state)
        
        for s in traj:
            print s.move_str() + " -> " + s.display_str()
        return traj
    # ------------------------------------------------------------------- step
    def step(self, ):
        """ Pour chaque etat, cherche tous les états suivants : faire bouger
tous les robots.
        """
        # Augmente la profondeur
        self._depth += 1
        self._explore = copy.copy(self._next)
        self._next = []
        while len(self._explore) > 0 :
            # Premier état à explorer
            state = self._explore.pop(0)
            # Ajoute à seen
            self._seen.append( state )
            print "STATE = " + state.display_str()


            # Sur le board, met les positions des robots
            self._bb.remove_rob()
            try:
                for rob in self._bb._robot:
                    rob.put( state._d_robot[rob._label] )
            except RobotPosError as rpe:
                print rpe.msg
            # Essaye de bouger les robots
            for rob in self._bb._robot:
                for dir in self._bb._go:
                    next_pos = self._bb._go[dir]( *rob._pos )
                    print "{0} at {1} {2} to {3}".format( rob._label, rob._pos, dir, next_pos )
                    if next_pos != rob._pos:
                        # Append to explore
                        # next_state = copy.deepcopy(state)
                        next_state = state.copy()
                        next_state._prev = state
                        next_state._d_robot[rob._label] = next_pos
                        next_state._rob = rob
                        next_state._dir = dir
                        print "Next state "+next_state.display_str()
                        # Atteint la cible -> on arrête
                        if self.target_reached( next_state ):
                            print "TARGET REACHED " + next_state.display_str()
                            self._goal = next_state
                            return
                        # Ajoute à explore si pas déjà vu ou a explorer
                        if self.not_in( next_state, self._explore) and self.not_in( next_state, self._seen) and self.not_in( next_state, self._next ):
                            self._next.append( next_state )
                            print "SEEN : " + self.list_str( self._seen )
                            print "EXPL : " + self.list_str( self._explore )
                            print "NEXT : " + self.list_str( self._next )
            
            


# ******************************************************************************
# ***************************************************************************
def affiche(widget):
    window = gtk.Window()
    window.resize(300,300)
    window.connect("delete-event", gtk.main_quit)
    widget.show()
    window.add(widget)
    window.present()
    gtk.main()
def run_bsearch():
    """
    """
    # un simple board avec 2 robots
    board = BO.create_board5()
    rob_r = Robot( board, col=(1,0,0), label="rr" )
    board._robot.append( rob_r )
    rob_r.put( (0,0) )
    rob_g = Robot( board, col=(0,1,0), label="rg" )
    board._robot.append( rob_g )
    rob_g.put( (2,2) )

    # Need a Target
    cible = Target( board, col=(1,0,0), label = "tr", l_robot=[rob_r] )
    board._target = cible
    cible.put( (3,3) )
    
    print "****** BOARD *****"
    print board.dump_cells()
    print "******************"

    bsearch = BroadSearch( board )
    print bsearch.status_str()
    
    while( len(bsearch._next) > 0 and bsearch._goal == None):
        print "***** STEP *****"
        bsearch.step()
        print bsearch.status_str()
        print "SEEN : " + bsearch.list_str( bsearch._seen )
        print "EXPL : " + bsearch.list_str( bsearch._explore )
        print "NEXT : " + bsearch.list_str( bsearch._next )
        # raw_input("Press Enter to continue...")


    if bsearch._goal is None :
        print "**** Pas de solution ****"
    else :
        print "***** SOLUTION *****"
        traj = bsearch.find_traj( bsearch._goal )
        sol = SolTree( board )
        sol.build_from_sol( traj )
        board._tree.append( sol )

    # Nous allons essayer d'afficher
    # Position de départ
    board.remove_rob()
    rob_r.put( (0,0) )
    rob_g.put( (2,2) )
    affiche(board)

if __name__ == '__main__':
    run_bsearch()


