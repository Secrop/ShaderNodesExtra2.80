
bl_info = {
    "name": "ShaderNodesExtra",
    "author": "Secrop",
    "version": (0, 1, 6),
    "blender": (2, 78, 0),
    "location": "Node",
    "description": "Tools for NodeGroups",
    "warning": "This is still is alpha testing. Although, the basic API is complete, please keep your original nodegroups as backup",
    "wiki_url": "",
    "category": "Node",
    }

import bpy
import os, sys, importlib
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom
from nodeitems_builtins import ShaderNewNodeCategory, node_tree_group_type, group_tools_draw, node_group_items
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import Nodes


#default menu entry if node doesn't have a draw_menu function
menu_def_id='SH_EXTRA'
menu_def_name='Custom Nodes'


def NodesPath():
    path=os.path.dirname(os.path.realpath(__file__)) + '/Nodes'
    return path

def exportNodetree(nodetree, bl_name, bl_label):
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
            flt="{0:.3f}".format(val)
            flt.rstrip('0')
            if flt.endswith('.'):
                flt+='0'
            result+=flt
        return result

    filepath=NodesPath() +'/' + bl_name + '.py'
    file=open(filepath, 'w')
    file.write('import bpy\n')
    file.write('from ShaderNodeBase import ShaderNodeBase\n\n')
    file.write('class ' + bl_name + '(ShaderNodeBase):\n\n')
    file.write('    bl_name=\'' + bl_name + '\'\n')
    file.write('    bl_label=\'' + bl_label + '\'\n')
    file.write('    bl_icon=\'NONE\'\n\n')
    file.write('    def defaultNodeTree(self):\n')
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
        file.write('        self.addInput(\'' + input.bl_socket_idname + '\', ')
        attrs=socketattrs(input)
        file.write('{')
        for i, attr in enumerate(attrs):
            val=value_get(input, attr)
            file.write('\'' + attr + '\':' + formatVal(val))
            if i<len(attrs)-1:
                file.write(', ')
        file.write('})\n')
    for output in nodetree.outputs:
        file.write('        self.addOutput(\'' + output.bl_socket_idname + '\', ')
        attrs=socketattrs(output)
        file.write('{')
        for i, attr in enumerate(attrs):
            val=value_get(output, attr)
            file.write('\'' + attr + '\':' + formatVal(val))
            if i<len(attrs)-1:
                file.write(', ')
        file.write('})\n')
    for link in nodetree.links:
        file.write('        self.addLink(\'' + link.from_socket.path_from_id() +'\', \'' + link.to_socket.path_from_id() + '\')\n')
    file.write('\n    def init(self, context):\n        self.setupTree()\n\n')
    file.write('    #def copy(self, node):\n\n')
    file.write('    #def free(self):\n\n')
    file.write('    #def socket_value_update(self, context):\n\n')
    file.write('    #def update(self):\n\n')
    file.write('    #def draw_buttons(self, context, layout):\n\n')
    file.write('    #def draw_buttons_ext(self, contex, layout):\n\n')
    file.write('    #def draw_label(self):\n\n')
    file.close()
    register_node(bl_name)
    return {'FINISHED'}

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

def register_node(node):
    module=importlib.import_module('Nodes.' + node)
    nodeclass=getattr(module, node)
    bpy.utils.register_class(nodeclass)
    if hasattr(nodeclass, 'draw_menu'):
        catid, catname = nodeclass.draw_menu()
    else:
        catid, catname = menu_def_id, menu_def_name
    node_menu_include(catid, catname, nodeclass)

def unregister_node(node):
    nodeclass=getattr(bpy.types, node)
    if hasattr(nodeclass, 'draw_menu'):
        catid, catname=nodeclass.draw_menu()
    else:
        catid, catname= menu_def_id, menu_def_name
    node_menu_exclude(catid, catname, nodeclass)
    bpy.utils.unregister_class(nodeclass)

def register_nodes():
    for node in Nodes.listNodes():
        register_node(node)

def unregister_nodes():
    for node in Nodes.listNodes():
        unregister_node(node)

def node_menu_include(catid, catname, node):
    index, ident, cat, mt, pt=getCategory(catid, catname)
    if cat:
        itemslist=list(cat.items(context=None))
        for item in itemslist:
            if item.nodetype==node.bl_name:
                return
        itemslist.append(NodeItem(node.bl_name))
        delCat(catid, catname)
    else:
        itemslist=[NodeItem(node.bl_name)]
    category=ShaderNewNodeCategory(catid, catname, items=itemslist)
    addCat(category, index=index)

def node_menu_exclude(catid, catname, node):
    index, ident, cat, mt, pt=getCategory(catid, catname)
    if cat:
        itemslist=list(cat.items(context=None))
        for i in itemslist:
            if i.nodetype==node.bl_name:
                itemslist.remove(i)
        delCat(catid, catname)
    if itemslist:
        category=ShaderNewNodeCategory(catid, catname, items=itemslist)
        addCat(category, index=index)

def getCategory(catid, catname):
    nc=nodeitems_utils._node_categories
    for ident in nc:
        for idx, category in enumerate(nc[ident][0]):
            if category.identifier==catid and category.name==catname:
                return idx, ident, category, nc[ident][2][idx], nc[ident][3][idx]
    return None, None, None, None, None

def delCat(catid, catname):
    index, ident, cat, mt, pt=getCategory(catid, catname)
    if cat:
        bpy.utils.unregister_class(mt)
        bpy.utils.unregister_class(pt)
        nodeitems_utils._node_categories[ident][0].remove(cat)
        nodeitems_utils._node_categories[ident][2].remove(mt)
        nodeitems_utils._node_categories[ident][3].remove(pt)

def addCat(category, ident='SHADER', index=None):
    def draw_node_item(self, context):
        layout = self.layout
        col = layout.column()
        for item in self.category.items(context):
            item.draw(item, col, context)
    mt = type("NODE_MT_category_" + category.identifier, (bpy.types.Menu,), {
        "bl_space_type": 'NODE_EDITOR',
        "bl_label": category.name,
        "category": category,
        "poll": category.poll,
        "draw": draw_node_item,
        })
    pt = type("NODE_PT_category_" + category.identifier, (bpy.types.Panel,), {
        "bl_space_type": 'NODE_EDITOR',
        "bl_region_type": 'TOOLS',
        "bl_label": category.name,
        "bl_category": category.name,
        "category": category,
        "poll": category.poll,
        "draw": draw_node_item,
        })
    bpy.utils.register_class(mt)
    bpy.utils.register_class(pt)
    if index:
        nodeitems_utils._node_categories[ident][0].insert(index, category)
        nodeitems_utils._node_categories[ident][2].insert(index, mt)
        nodeitems_utils._node_categories[ident][3].insert(index, pt)
    else:
        nodeitems_utils._node_categories[ident][0].append(category)
        nodeitems_utils._node_categories[ident][2].append(mt)
        nodeitems_utils._node_categories[ident][3].append(pt)

def configBlender():
    def new_node_group_items(context):
        if context is None:
            return
        space = context.space_data
        if not space:
            return
        ntree = space.edit_tree
        if not ntree:
            return

        yield NodeItemCustom(draw=group_tools_draw)

        def contains_group(nodetree, group):
            if nodetree == group:
                return True
            else:
                for node in nodetree.nodes:
                    if node.bl_idname in node_tree_group_type.values() and node.node_tree is not None:
                        if contains_group(node.node_tree, group):
                            return True
            return False

        for group in context.blend_data.node_groups:
            if group.bl_idname != ntree.bl_idname:
                continue
            # filter out recursive groups
            if contains_group(group, ntree):
                continue
            # filter hidden shadertrees
            if group.is_hidden:
                continue
            yield NodeItem(node_tree_group_type[group.bl_idname],
                           group.name,
                           {"node_tree": "bpy.data.node_groups[%r]" % group.name})

    if not hasattr(bpy.types.ShaderNodeTree, 'is_hidden'):
        bpy.types.ShaderNodeTree.is_hidden=bpy.props.BoolProperty(name="is_hidden", description="Returns True if the node tree is hidden", default=False)
    bpy.types.NODE_MT_category_SH_NEW_GROUP.category.items=new_node_group_items
    bpy.types.NODE_PT_category_SH_NEW_GROUP.category.items=new_node_group_items

def revertBlender():
    #leaving the is_hidden property on the ShaderNodeTree, as it is harmless.
    bpy.types.NODE_MT_category_SH_NEW_GROUP.category.items=node_group_items
    bpy.types.NODE_PT_category_SH_NEW_GROUP.category.items=node_group_items

def register():
    #to hide nodes private trees from the group menu, uncomment the following line, and the revertBlender in unregister()
    configBlender()
    bpy.utils.register_class(NodeGroupConvert)
    register_nodes()

def unregister():
    revertBlender()
    bpy.utils.unregister_class(NodeGroupConvert)
    unregister_nodes()

if __name__ == "__main__":
    register()
