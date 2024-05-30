# -*- coding: utf-8 -*-
"""
Created on Wed May 29 19:10:08 2024

@author: bjans
"""
import re
from collections import namedtuple

#EDIT:
INPUT_PATH = r"C:\Users\bjans\Downloads\Z_gradient.gcode"
TYPE_COMMENT = ";TYPE:"
IGNORE_TYPE = [";TYPE:Support material", ";TYPE:Skirt/Brim",
               ";TYPE:Support material interface", ";TYPE:Custom"] #prusa
LAYER_CHANGE = ";LAYER_CHANGE"
READ_M221 = True # use M221 to consider as flow factor
#EDIT END

ignore = False
E_layer = 0
E_total = 0
Z = 0

X_Y = [[], []]
CoG = []
after_layer_change = False
retr = False
de_retr = 0
retr_d = 0
E_factor = 1

Point2D = namedtuple('Point2D', 'x y')
last_pos = Point2D(0,0)

prog_X = re.compile(r"X(\d*\.?\d*)")
prog_Y = re.compile(r"Y(\d*\.?\d*)")
prog_Z = re.compile(r"Z(\d*\.?\d*)")
prog_E = re.compile(r"E(.?\-*\d*\.?\d*)")
prog_S = re.compile(r"S(\d*\.?\d*)")
prog_G = re.compile(r"^G[0-1]")

prog_move = re.compile(r'^G[0-1].*X.*Y')

# this function comes from: https://github.com/CNCKitchen/GradientInfill/blob/master/addGradientInfill.py
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
            ignore = False
            for unwanted_type in IGNORE_TYPE: 
                if current_line.startswith(unwanted_type):
                    ignore = True
                    break
            continue
            
        
        if current_line.startswith(LAYER_CHANGE):
            # when list is not empty 
            if len(X_Y[0]) + len(X_Y[1]) > 0:
                CoG.append([(sum(X_Y[0]), sum(X_Y[1])), Z * E_layer])
            # reset layer list
            X_Y = [[], []]
            E_layer = 0
            after_layer_change = True
        
        if READ_M221 and current_line.startswith("M221"):
            E_factor = float(prog_S.search(current_line).group(1)) / 100
            continue
        
        if prog_G.match(current_line):
            Z_move = prog_Z.search(current_line)
            if after_layer_change and Z_move:
                Z = float(Z_move.group(1))
                after_layer_change = False
                
            if prog_move.search(current_line):
                pos = getXY(current_line)
                
                # relevant gcode
                if not ignore:
                    if "E" in current_line:
                        E = float(prog_E.search(current_line).group(1))
                        if E < 0:
                            retr = True
                            retr_d += abs(E)
                            de_retr = 0
                            last_pos = pos
                            continue
                        elif retr:
                            de_retr += E
                            if de_retr >= retr_d:
                                retr = False
                                retr_d = 0
                                last_pos = pos
                                continue
                                
                        E_layer += E * E_factor
                        E_total += E * E_factor
                        
                        middle = middle_point(last_pos, pos)
                        for i in range(2):
                            X_Y[i].append(middle[i] * E * E_factor)
            
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