# Center of Gravity Gcode
## Introduction:
This python script can calculate the Center of gravity from the gcode. It can ignore unwanted objects in the gcode like support, skirt brim etc.
To do so it needs comments from the gcode, which mark an unwanted feature type.
I set it up to work with gcode generated by Prusa slicer. It can be adopted to other slicer, if they have similar comments (orca slicer for example).

Currently there seems to be an issue with supports, which seem to influence the coordinate of the CoG but shouldn't.
### How to operate: 
1. check, that your gcode is compatible with the requirements 
2. change the path to your gcode file to ``INPUT_PATH``
3. change the comments to suit your gcode (set up for Prusa slicer)
4. run the script (it may take a few seconds)
5. the output of the script will be in the coordinates of the gcode file (your printer)

You won't have a graphical representation, where the CoG is. I recommend to open a gcode viewer and find the coordinate there.

### Requirements:
- only G1 and G0 commands
- only absolute movements
- only relative E
- planar slicing
- one material (same density)

## Derivation of the formula to calculate the CoG:
$$x_{s_{layer}} = \frac{\sum_{i}x_{i}*V_{i}}{\sum_{i}V_{i}}$$
$$x_{s_{total}} = \frac{\sum_{layer}(\frac{\sum_{i}x_{i}*V_{i}}{\sum_{i}V_{i}})*V_{layer}}{\sum_{layer}V_{layer}}$$
$$V_{layer} = \sum_{i}V_{i}$$
$$x_{s_{total}} = \frac{\sum_{layer}(\sum_{i}x_{i}*V_{i})}{\sum_{layer}V_{layer}}$$
$$V_{cylinder} = \pi*r^2*E$$
$$E:= h$$
$$x_{s_{total}} = \frac{\sum_{layer}(\sum_{i}x_{i}*E_{i})}{\sum_{layer}E_{layer}}$$
[source](https://en.wikipedia.org/w/index.php?title=Special:MathWikibase&qid=Q2945123)