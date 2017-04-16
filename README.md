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
