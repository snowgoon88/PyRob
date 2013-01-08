#!/usr/bin/python
# -*- coding: utf-8 -*-

# ******************************************************************************
# ************************************************************************* Cell
# ******************************************************************************
class Cell(object):
    """
    Une Cell a:
    - une position (_pos=(x,y)),
    - un type (_type = 'void','forbid','corner',... )
    - peut contenir un robot (_rob)
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
        self._rob = None
        self._values = {}

    # ---------------------------------------------------------------------- str
    def __str__(self):
        """
        Représentation comme str d'une Cell.
        """
        rob_str = ''
        if self._rob <> None:
            rob_str = ' ('+self._rob._label+') '
        return self._pos.__str__()+" ["+self._type+"] "+rob_str+"values="+self._values.__str__()

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------- todo
    def has_rob(self, ):
        """Un robot sur la Cell ?
        """
        return self._rob != None

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
# ************************************************************************** END
# ******************************************************************************
