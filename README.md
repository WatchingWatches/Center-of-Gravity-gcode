# Center of Gravity Gcode (FDM)
## Introduction:
This python script can calculate the Center of gravity from the gcode. It can ignore unwanted objects in the gcode like support, skirt brim etc.
To do so it needs comments from the gcode, which mark an unwanted feature type.
I set it up to work with gcode generated by Prusa slicer. It can be adopted to other slicer, if they have similar comments (orca slicer for example).

The Prusa gcode viewer already has a built in function to calculate the CoG and display the coordinates.
Many other gcode viewer however don't have this function. When you use the Prusa gcode viewer with gcode generated by another slicer, it won't recognize all of the feature types
and calculate the CoG with supports. This script allows to adapt to any gcode with comments regarding the feature type.
I also added an option to consider M221 commands as an flow factor, which is not done by gcode viewers, because normally this command is interpreted by your printers firmware.
To enable this feature set ``READ_M221 = True``. 
This script gives you the freedom to implement these kind of niche applications.

### How to operate: 
1. check, that your gcode is compatible with the requirements 
2. change the path to your gcode file to ``INPUT_PATH``
3. change the comments to suit your gcode (set up for Prusa slicer)
4. run the script (it may take a few seconds)
5. the output of the script will be in the coordinates of the gcode file (your printer)

You won't have a graphical representation, where the CoG is. I recommend to open a gcode viewer and find the coordinate there.

### Requirements / Slicer setup:
- only G1 and G0 commands (you will get a warning)
- only absolute movements
- only relative E
- planar slicing
- one material (same density)
- one object

## Derivation of the formula to calculate the CoG:
$$x_{s_{layer}} = \frac{\sum_{i}x_{i}*V_{i}}{\sum_{i}V_{i}}$$
$$x_{s_{total}} = \frac{\sum_{layer}(\frac{\sum_{i}x_{i}*V_{i}}{\sum_{i}V_{i}})*V_{layer}}{\sum_{layer}V_{layer}}$$
$$V_{layer} = \sum_{i}V_{i}$$
$$x_{s_{total}} = \frac{\sum_{layer}(\sum_{i}x_{i}*V_{i})}{\sum_{layer}V_{layer}}$$
$$V_{cylinder} = \pi * r^2 * E$$
$$E := h$$
$$x_{s_{total}} = \frac{\sum_{layer}(\sum_{i}x_{i}*E_{i})}{\sum_{layer}E_{layer}}$$
[Source](https://en.wikipedia.org/w/index.php?title=Special:MathWikibase&qid=Q2945123)

To make the script efficient the X/Y-CoG of each layer gets calculated and saved for each layer (this way you could modify the script to see the CoG changing every layer).
 At the end the final CoG gets calculated based on all layers.

The Z-CoG gets calculated with the first formula.

### Assumptions:
Each extruded line is symmetric, so the X/Y-CoG is in the middle of the line.
The Z-CoG is in the middle of the layer.