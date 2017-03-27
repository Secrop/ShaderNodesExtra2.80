bl_info = {
    "name": "ShaderNodesExtra",
    "author": "Secrop",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Node",
    "description": "Tools for NodeGroups",
    "warning": "",
    "wiki_url": "",
    "category": "Node",
    }
    
import bpy
import os, sys, importlib

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import Nodes

forbidden_nodes=['ShaderNodeTexImage','ShaderNodeTexEnviroment','ShaderNodeTexSky', 'ShaderNodeMapping']
nodes_with_from_dupli=['ShaderNodeTexCoord', 'ShaderNodeUVMap']
nodes_with_distribution=['ShaderNodeBsdfGlossy', 'ShaderNodeBsdfRefraction', 'ShaderNodeBsdfGlass', 'ShaderNodeBsdfAnisotropic']
nodes_with_falloff=['ShaderNodeSubsurfaceScattering']
nodes_with_component=['ShaderNodeBsdfToon', 'ShaderNodeBsdfHair']
nodes_with_operation=['ShaderNodeMath', 'ShaderNodeVectorMath']
nodes_with_blend_type=['ShaderNodeMixRGB']
nodes_with_clamp=['ShaderNodeMixRGB', 'ShaderNodeMath']
nodes_with_outputs=['ShaderNodeRGB', 'ShaderNodeValue', 'ShaderNodeNormal']
nodes_with_pixel_size=['ShaderNodeWireframe']


def socketattrs(socket):
    items=['name']
    if socket.bl_socket_idname!='NodeSocketShader':
        items.append('default_value')
        if socket.bl_socket_idname!='NodeSocketColor' and socket.bl_socket_idname!='NodeSocketBool':
            items.append('min_value')
            items.append('max_value')
    return items        
        

def nodesattrs(node):
    nodeinstance=node.bl_idname
    items=['name']
    if nodeinstance in nodes_with_from_dupli:
        items.append('from_dupli')   
    if nodeinstance in nodes_with_distribution:
        items.append('distribution')
    if nodeinstance in nodes_with_falloff:
        items.append('falloff')
    if nodeinstance in nodes_with_component:
        items.append('component')
    if nodeinstance in nodes_with_operation:
        items.append('operation')
    if nodeinstance in nodes_with_blend_type:
        items.append('blend_type')
    if nodeinstance in nodes_with_clamp:
        items.append('use_clamp')
    if nodeinstance in nodes_with_pixel_size:
        items.append('use_pixel_size')
    if nodeinstance in nodes_with_outputs:
        items.append('outputs[0]')
        return items
    for input in node.inputs:
        if input.is_linked==False and input.bl_idname!='NodeSocketShader':
            items.append(input.path_from_id().rsplit(".",1)[1] + '.default_value')
    return items           

def getpath(obj, path):
    if "." in path:
        path_prop, path_attr = path.rsplit(".", 1)
        prop = obj.path_resolve(path_prop)
    else:
        prop = obj
        path_attr = path
    return prop, path_attr
    
def value_get(obj, path):
    prop, path_attr=getpath(obj, path)
    return getattr(prop, path_attr)

def NodesPath():
    path=os.path.dirname(os.path.realpath(__file__)) + '\\Nodes'
    return path
	
def formatVal(val):
    result=''
    if str(type(val))=="<class 'bpy_prop_array'>": #this is really ugly!
        result+='['
        for n, comp in enumerate(val):
            result+="{0:.3f}".format(comp)
            if n < len(val)-1:
                result+=','
            else:
                result+=']'
    elif str(type(val))=="<class 'str'>":  
            result+='\'' + val + '\''
    else:
            result+="{0:.3f}".format(val)
    return result			

def exportNodetree(nodetree, bl_name, bl_label):
    filepath=NodesPath() +'\\' + bl_name + '.py'
    file=open(filepath, 'w')
    file.write('import bpy\n')
    file.write('from Nodes.ShaderNodeBase import ShaderNodeBase\n\n')
    file.write('class ' + bl_name + '(bpy.types.NodeCustomGroup, ShaderNodeBase):\n\n')
    file.write('    bl_name=\'' + bl_name + '\'\n')
    file.write('    bl_label=\'' + bl_label + '\'\n')
    file.write('    bl_icon=\'NONE\'\n\n')
    file.write('    def defaultNodetree(self, name):\n')
    file.write('        self.node_tree=bpy.data.node_groups.new(name + \'_nodetree\', \'ShaderNodeTree\')\n')
    file.write('        try:\n            self.node_tree.is_hidden=True\n        except:\n            print(\'cannot find attribute(is_hidden) in Nodetree\')\n')
    file.write('        self.addNode(\'NodeGroupInput\', {\'name\':\'Group Input\'})\n')
    file.write('        self.addNode(\'NodeGroupOutput\', {\'name\':\'Group Output\'})\n')
    #Write Nodes creation functions
    for node in nodetree.nodes:
        if node.bl_idname!='NodeGroupInput' and node.bl_idname!='NodeGroupOutput':
            file.write('        self.addNode(\'' + node.bl_idname + '\', ')
            file.write('{')
            attrs=nodesattrs(node)
            for i, attr in enumerate(attrs):
                val=value_get(node, attr)
                file.write('\'' + attr + '\':' + formatVal(val))
                if i<len(attrs)-1:
                    file.write(', ')
            file.write('})\n') 
    for input in nodetree.inputs:
        file.write('        self.addSocket(False, \'' + input.bl_socket_idname + '\', ')
        attrs=socketattrs(input)
        file.write('{')
        for i, attr in enumerate(attrs):
            val=value_get(input, attr)
            file.write('\'' + attr + '\':' + formatVal(val))
            if i<len(attrs)-1:
                file.write(', ')
        file.write('})\n')             
    for output in nodetree.outputs:
        file.write('        self.addSocket(True, \'' + output.bl_socket_idname + '\', ')
        attrs=socketattrs(output)
        file.write('{')
        for i, attr in enumerate(attrs):
            val=value_get(output, attr)
            file.write('\'' + attr + '\':' + formatVal(val))
            if i<len(attrs)-1:
                file.write(', ')
        file.write('})\n')                         
    for link in nodetree.links:
        file.write('        self.innerLink(\'' + link.from_socket.path_from_id() +'\', \'' + link.to_socket.path_from_id() + '\')\n')
    file.write('\n    def init(self, context):\n        self.getNodetree()\n\n')
    file.write('    #def copy(self, node):\n\n')
    file.write('    #def free(self):\n\n')
    file.write('    #def socket_value_update(self, context):\n\n')
    file.write('    #def update(self):\n\n')            
    file.write('    #def draw_buttons(self, context, layout):\n\n')            
    file.write('    #def draw_buttons_ext(self, contex, layout):\n\n')
    file.write('    #def draw_label(self):\n\n')
    file.close()
    update_nodes(bl_name)
    return {'FINISHED'}

def update_nodes(ignore_node=''):
    unregister_nodes(ignore_node)
    register_nodes()

class NodeGroupConvert(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "node.convert_nodegroup"
    bl_label = "Convert Selected NodeGroup to PyNode"
    bl_options = {'REGISTER', 'UNDO'}

    nodename=bpy.props.StringProperty(name="bl_name", default="")
    nodelabel=bpy.props.StringProperty(name="bl_label", default="")
    
    @classmethod
    def poll(cls, context):
        space = context.space_data
        currentNode = context.active_node
        return space.type == 'NODE_EDITOR' and currentNode.type=='GROUP'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
        
    def execute(self, context):
        return exportNodetree(context.active_node.node_tree.id_data, self.nodename, self.nodelabel)


import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class ShaderNodesExtraCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return (context.space_data.tree_type == 'ShaderNodeTree' and
                context.scene.render.use_shading_nodes)


def register_nodes():
    itemlist=[]
    for node in Nodes.listNodes():
        module=importlib.import_module('Nodes.' + node)
        nodeclass=getattr(module, node)
        bpy.utils.register_class(nodeclass)    
        itemlist.append(NodeItem(node))
    if itemslist:
        node_categories=[ShaderNodesExtraCategory("SH_EXTRA", "Custom Nodes", items=itemlist)]    
        nodeitems_utils.register_node_categories("Custom Nodes", node_categories)    

def unregister_nodes(ignore=''):            
    for node in Nodes.listNodes():
        if node!=ignore:
            bpy.utils.unregister_class(getattr(bpy.types, node))    
    nodeitems_utils.unregister_node_categories("Custom Nodes")

def register():
    bpy.utils.register_class(NodeGroupConvert)
    register_nodes()





def unregister():
    bpy.utils.unregister_class(NodeGroupConvert)
    unregister_nodes()



if __name__ == "__main__":
    register()

