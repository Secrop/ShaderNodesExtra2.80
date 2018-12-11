
This version is for Blender2.80

ATM, there are some issues with nodes categories, as they are shared with Eevee. Still don't know how to solve this but I'll figure it out.
(Note that these nodes don't work with Eevee. They lack a proper pointer to the gpufunc()!!)

Another problem is the abnormal recreation of nodetrees in 2.80. I think it's a bug in Blender... Need to profile this error.

# ShaderNodesExtra
Utilities for Cycles PyNodes

This Addon serves the purpose of simplifying the creation of new custom nodes for Cycles, and it can be considered as a better API for custom nodes.
The nodes produced by this addon are GPU compatible, and internally they work as an ordinary nodegroup. The main difference is that it's possible to change completly the node layout and add functionality to the node.

Most of it will work in background, and visibly there's not much to see yet.

Apart from the typical node functions (draw_buttons, draw_buttons_ext, update, free, copy, etc), the nodes integrate the following API(s):

ShaderNodeBase API:
  addNode(nodeType, **nodeAttributes)
  delNode(node)
  addInput(socketType, **socketAttributes)
  delInput(socket)
  addOutput(socketType, **socketAttributes)
  delOutput(socket)
  addLink(socket, socket)
  delLink(link)

Nodes created with this API should call setupTree() in the init() function, and should have a defaultNodeTree() to define the initial node configuration.

For now, while there isn't any MenuEditor, nodes are in charged to define their menu categories. This is not a good approach as a design perspective, and editing the menu will soon become something aside from the custom nodes.

The addon includes a converter operator, that can automatically write a custom node based in some nodegroup.
To use it, select the nodegroup you want to convert into a script, press SPACE and look for 'Convert Selected Nodegroup to PyNode'. It will prompt for a bl_name and a bl_label. For consistency, bl_name should start by 'ShaderNode', thouhgt there's nothing to stop one from naming it whatever they want.
The node will be automatically added to the 'Custom Nodes' category, and to change this, one should add a draw_menu function to the node script (located in the 'Nodes' folder inside the Addon path).

At the moment, I'm also sharing some nodes with the purpose to show what is possible..

-DisplacementBake: is a node to help baking displacement maps in a similar fashion as in ZBrush. (Credits to nudelZ)

-NormalBake: will help the creation of tangent normal maps from a normal vector.

-SwitchFloat: is a simple switch, if the 'Switch' input is set to 0, the output will be the 'value1'; if 1, the output will be 'value2'

-Compare: this node will compare two values and return a boolean. It features '>', '>=', '==', '!=', '<=', '<' and '~='.

-Interpolate: as the name says, it will interpolate between two values. Defaults to Lerp(linear interpolation), but also features 'SmoothStep', 'SmootherStep', 'HighPower' and its inverse, 'Sine' and its inverse, 'Cosine' and 'Catmull-Rom' interpolations.

-Loop: A more complex node that uses a nodegroup as a loop step. The nodegroup requires to have an input socket named 'iterator' for feeding the node with the step integer, and at least 1 output with the same name as the input for the data that is trasnfer from each cycle to the next.
