#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 19:10:08 2024
License: MIT
@author: Benedikt Jansson - WatchingWatches
"""
import re
from collections import namedtuple
from colorama import Fore, Style

Point2D = namedtuple('Point2D', 'x y')
Point3D = namedtuple('Point3D', 'x y z')

#EDIT:
INPUT_PATH = r"C:\Users\bjans\Downloads\xbox_stealth_stand_53m_0.16mm_200C_PLA_ENDER5PRO.gcode"
TYPE_COMMENT = ";TYPE:"
IGNORE_TYPE = [";TYPE:Support material", ";TYPE:Skirt/Brim",
               ";TYPE:Support material interface", ";TYPE:Custom"] #prusa
LAYER_CHANGE = ";LAYER_CHANGE"
READ_M221 = True # use M221 to consider as flow factor
Coordinate_origin = Point3D(0, 0, 0) # define an origin for coordinate system (default 0,0,0 := same as gcode)
#EDIT END

ignore = False
E_layer = 0
E_total = 0
Z = 0
last_Z = 0

X_Y = [0, 0]
CoG = []
after_layer_change = False
retr = False
de_retr = 0
retr_d = 0
E_factor = 1


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
        
        # stop program if G2/3 movements are detected
        if current_line.startswith("G2 ") or current_line.startswith("G3 "):
            # in some IDE's the second method doesn't work
            print(Fore.RED +"\033[91mWARNING: G2/3 movements are not supported!\033[0m")
            print(Fore.RED +"\033[91mPlease change the gcode to only use G0/1 movements\033[0m")
            print(Fore.RED +"\033[91mThe output CoG is incorrect!\033[0m")
            print(Style.RESET_ALL)
            print(Fore.MAGENTA + current_line)
            print(Style.RESET_ALL)
            break    
        # TODO: mit enumerate ende der schleife dann end obsolet
        if current_line.startswith(LAYER_CHANGE) or current_line.startswith(";End gcode"):
            # when list is not empty 
            if X_Y[0] + X_Y[1] > 0:
                # Z CoG is in the middle of the layer
                CoG.append([[X_Y[0], X_Y[1]], round(Z - (Z-last_Z)/2, 3) * E_layer])
            # reset layer list
            X_Y = [0, 0]
            E_layer = 0
            last_Z = Z
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
                            X_Y[i] += middle[i] * E * E_factor
            
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

X_CoG -= Coordinate_origin[0]
Y_CoG -= Coordinate_origin[1]
Z_CoG -= Coordinate_origin[2]

print("Gcode file:", INPUT_PATH)
print("CoG: X{} Y{} Z{}".format(X_CoG, Y_CoG, Z_CoG))
print(f"Coordinate System origin X:{Coordinate_origin[0]} Y:{Coordinate_origin[1]} Z:{Coordinate_origin[2]}")