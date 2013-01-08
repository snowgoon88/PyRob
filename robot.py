#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
# ******************************************************************************
# ************************************************************************* TODO
# ******************************************************************************
class Robot(object):
    """
    Un robot a une _pos et une _color.
    """
    
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def __init__(self, board, col=(1,0,0), label="rr"):
        """
        Un robot, associé à une Board.
        """
        self._label = label
        self._board = board
        self._color = col
        self._pos = None

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def put(self, pos):
        """
        Pose le robot sur Board, màj Cell (_label)
        :Param
        - `pos`: (x,y)
        """
        # Cell doit pas être "forbid" ou avoir un robot
        cell = self._board.get_cell( pos )
        if cell._type.startswith( ('f','r') ) or cell.has_rob(): 
            raise RobotPosError( cell )
        # Pose le robot
        cell._rob = self
        self._pos = cell._pos
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def remove(self, ):
        """Enlève le robot du Board.
        """
        if self._pos != None:
            cell = self._board.get_cell( pos )
            cell._rob = None
            self._pos = None

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def draw(self, cr):
        """
        :Param
        - `cr`: Cairo context
        """
        if self._pos <> None :
            cr.set_source_rgb( *self._color )
            cr.arc( self._pos[0], self._pos[1], 0.3, 0, math.pi*2 )
            cr.fill()
        
# ******************************************************************************
# ************************************************************************* TODO
# ******************************************************************************
class RobotPosError(Exception):
    """Robot badly placed
    """
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def __init__(self, cell):
        """Crée le msg erreur
        :Param
        - `cell`: Cell
        """
        Exception.__init__( 'Rob mal placé pos={0}, type={1}, rob={2}'.format( cell._pos, cell._type, cell._rob))

# ******************************************************************************
# ************************************************************************** END
# ******************************************************************************
        

        
        
