# -*- coding: utf-8 -*-
"""
Created on Wed May 29 19:10:08 2024

@author: bjans
"""
import re
from collections import namedtuple

#EDIT:
INPUT_PATH = r"C:\Users\bjans\Downloads\Shape-Box_50m_0.20mm_200C_PLA_ENDER5PRO.gcode"
TYPE_COMMENT = ";TYPE:"
IGNORE_TYPE = [";TYPE:Support material", ";TYPE:Skirt/Brim",
               ";TYPE:Support material interface", ";TYPE:Custom"] #prusa
LAYER_CHANGE = ";LAYER_CHANGE"

#EDIT END

ignore = True
E_layer = 0
E_total = 0
Z = 0

X_Y = [[], []]
CoG = []
after_layer_change = False

Point2D = namedtuple('Point2D', 'x y')
last_pos = Point2D(0,0)

prog_X = re.compile(r"X(\d*\.?\d*)")
prog_Y = re.compile(r"Y(\d*\.?\d*)")
prog_Z = re.compile(r"Z(\d*\.?\d*)")
prog_E = re.compile(r"E(\d*\.?\d*)")
prog_G = re.compile(r"^G[0-1]")

prog_move = re.compile(r'^G[0-1].*X.*Y')

def getXY(currentLine: str) -> Point2D:
    """Create a ``Point2D`` object from a gcode line.

    Args:
        currentLine (str): gcode line

    Raises:
        SyntaxError: when the regular expressions cannot find the relevant coordinates in the gcode

    Returns:
        Point2D: the parsed coordinates
    """
    searchX = prog_X.search(currentLine)
    searchY = prog_Y.search(currentLine)
    if searchX and searchY:
        elementX = searchX.group(1)
        elementY = searchY.group(1)
    else:
        raise SyntaxError(f'Gcode file parsing error for line {currentLine}')

    return Point2D(float(elementX), float(elementY))

def middle_point(point_1: Point2D, point_2: Point2D)-> Point2D:
    """Calculate middle point
    
    Args:
        point_1 (Point2D): point 1
        point_2 (Point2D): point 2
        
    Returns:
        Point2D: the coordinates of the middle point
    """
    d_x = point_2[0] - point_1[0]
    d_y = point_2[1] - point_1[1]
    
    return Point2D(point_2[0] - d_x/2, point_2[1] - d_y/2)

with open(INPUT_PATH, "r") as gcodeFile:
    for current_line in gcodeFile:
        if current_line.startswith(TYPE_COMMENT):
            for unwanted_type in IGNORE_TYPE: 
                if current_line.startswith(unwanted_type):
                    ignore = True
                    continue
                
            ignore = False
        
        if current_line.startswith(LAYER_CHANGE):
            # when list is not empty 
            if len(X_Y[0]) + len(X_Y[1]) > 0:
                CoG.append([(sum(X_Y[0]), sum(X_Y[1])), Z * E_layer])
                pass
            # reset layer list
            X_Y = [[], []]
            E_layer = 0
            after_layer_change = True
        
        if prog_G.match(current_line):
            Z_move = prog_Z.search(current_line)
            if after_layer_change and Z_move:
                Z = float(Z_move.group(1))
                
            if prog_move.search(current_line):
                pos = getXY(current_line)
                
                # relevant gcode
                if not ignore:
                    if "E" in current_line:
                        E = float(prog_E.search(current_line).group(1))
                        E_layer += E
                        E_total += E
                        #TODO retractions
                        
                        middle = middle_point(last_pos, pos)
                        for i in range(2):
                            X_Y[i].append(middle[i] * E)
            
                last_pos = pos

X_CoG = 0
Y_CoG = 0
Z_CoG = 0
# calculate final CoG
for layer in CoG:
    X_CoG += layer[0][0]
    Y_CoG += layer[0][1]
    Z_CoG += layer[1] 

X_CoG /= E_total
Y_CoG /= E_total
Z_CoG /= E_total

print("CoG: X{} Y{} Z{}".format(X_CoG, Y_CoG, Z_CoG))