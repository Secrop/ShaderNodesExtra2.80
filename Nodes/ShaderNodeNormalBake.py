
#
#   Node Authors: nudelZ, Secrop
#
#   Node Description: Utility node for baking various Displacement maps
#
#   version: (0,1,0)
#

import bpy

class ShaderNodeNormalBake(bpy.types.NodeCustomGroup):

    bl_name='ShaderNodeNormalBake'
    bl_label='Normal Bake'
    bl_icon='NONE'

    def __path_resolve__(self, obj, path):
        if "." in path:
            extrapath, path= path.rsplit(".", 1)
            obj = obj.path_resolve(extrapath)
        return obj, path
            
    def value_set(self, obj, path, val):
        obj, path=self.__path_resolve__(obj, path)
        setattr(obj, path, val)                

    def addNodes(self, nodes):
        for nodeitem in nodes:
            node=self.node_tree.nodes.new(nodeitem[0])
            for attr in nodeitem[1]:
                self.value_set(node, attr, nodeitem[1][attr])

    def addLinks(self, links):
        for link in links:
            if isinstance(link[0], str):
                if link[0].startswith('inputs'):
                    socketFrom=self.node_tree.path_resolve('nodes["Group Input"].outputs' + link[0][link[0].rindex('['):])
                else:
                    socketFrom=self.node_tree.path_resolve(link[0])
            if isinstance(link[1], str):
                if link[1].startswith('outputs'):
                    socketTo=self.node_tree.path_resolve('nodes["Group Output"].inputs' + link[1][link[1].rindex('['):])
                else:
                    socketTo=self.node_tree.path_resolve(link[1])
            self.node_tree.links.new(socketFrom, socketTo)

    def addInputs(self, inputs):
        for inputitem in inputs:
            name = inputitem[1].pop('name')
            socketInterface=self.node_tree.inputs.new(inputitem[0], name)
            socket=self.path_resolve(socketInterface.path_from_id())
            for attr in inputitem[1]:
                if attr in ['default_value', 'hide', 'hide_value']:
                    self.value_set(socket, attr, inputitem[1][attr])
                else:
                    self.value_set(socketInterface, attr, inputitem[attr])
            
    def addOutputs(self, outputs):
        for outputitem in outputs:
            name = outputitem[1].pop('name')
            socketInterface=self.node_tree.outputs.new(outputitem[0], name)
            socket=self.path_resolve(socketInterface.path_from_id())
            for attr in outputitem[1]:
                if attr in ['default_value']:
                    self.value_set(socket, attr, outputitem[1][attr])
                else:
                    self.value_set(socketInterface, attr, outputitem[1][attr])    

    axis_items=(('X', 'X', 'POS_X'),
        ('-X', '-X', 'NEG_X'),
        ('Y', 'Y', 'POS_Y'),
        ('-Y', '-Y', 'NEG_Y'),
        ('Z', 'Z', 'POS_Z'),
        ('-Z', '-Z', 'NEG_Z'))
    
    def axisupdate(self, context):
        if (self.axis_X.lstrip('-')==self.axis_Y.lstrip('-')) or (self.axis_X.lstrip('-')==self.axis_Z.lstrip('-')) or (self.axis_Y.lstrip('-')==self.axis_Z.lstrip('-')):
            return
        for i, cmp in enumerate([self.axis_X, self.axis_Y, self.axis_Z]):
            orig=['X','Y','Z'].index(cmp.lstrip('-'))
            if cmp.startswith('-'):
                fromsocket=self.node_tree.nodes['Negative'].outputs[orig]
            else:
                fromsocket=self.node_tree.nodes['Positive'].outputs[orig]
            tosocket=self.node_tree.nodes['FinalCombine'].inputs[i]
            if tosocket.is_linked:
                self.node_tree.links.remove(tosocket.links[0])
            self.node_tree.links.new(fromsocket, tosocket)    

    def uvmapupdate(self, context):
        self.node_tree.nodes['Tangent'].uv_map=self.uvmap
            
    axis_X = bpy.props.EnumProperty(default = 'X', items = axis_items, name = "X_list", update = axisupdate)
    axis_Y = bpy.props.EnumProperty(default = 'Y',items = axis_items, name = "Y_list", update = axisupdate)
    axis_Z = bpy.props.EnumProperty(default = 'Z',items = axis_items, name = "Z_list", update = axisupdate)                                                 
    uvmap = bpy.props.StringProperty(name = 'UV Map',default = '', update = uvmapupdate)

    def init(self, context):
        self.node_tree = bpy.data.node_groups.new(self.bl_name+'nodetree', 'ShaderNodeTree')
        self.node_tree.is_hidden=True
        self.addNodes([('NodeGroupInput', {'name':'Group Input'}),
            ('NodeGroupOutput', {'name':'Group Output'}),
            ('ShaderNodeNewGeometry', {'name':'Geometry'}),
            ('ShaderNodeTangent', {'name':'Tangent', 'direction_type':'UV_MAP'}),
            ('ShaderNodeVectorMath', {'name':'CoTangent', 'operation':'CROSS_PRODUCT'}),
            ('ShaderNodeVectorMath', {'name':'YDot', 'operation':'DOT_PRODUCT'}),
            ('ShaderNodeVectorMath', {'name':'ZDot', 'operation':'DOT_PRODUCT'}),
            ('ShaderNodeCombineXYZ', {'name':'Combine XYZ'}),
            ('ShaderNodeVectorMath', {'name':'XDot', 'operation':'DOT_PRODUCT'}),
            ('ShaderNodeMixRGB', {'name':'Scale', 'blend_type':'MULTIPLY', 'inputs[0].default_value':1.0, 'inputs[2].default_value':[0.5,0.5,0.5,1.0]}),
            ('ShaderNodeMixRGB', {'name':'Translate', 'blend_type':'ADD', 'inputs[0].default_value':1.0, 'inputs[2].default_value':[0.5,0.5,0.5,1.0]}),
            ('ShaderNodeInvert', {'name':'Invert', 'inputs[0].default_value':1.000}),
            ('ShaderNodeSeparateRGB', {'name':'Negative'}),
            ('ShaderNodeSeparateRGB', {'name':'Positive'}),
            ('ShaderNodeCombineRGB', {'name':'FinalCombine', 'inputs[0].default_value':0.000, 'inputs[1].default_value':0.000, 'inputs[2].default_value':0.000}),
            ('ShaderNodeEmission', {'name':'EmiClosure', 'inputs[1].default_value':1.0})])       
        self.addInputs([('NodeSocketVector', {'name':'Normal', 'hide_value':True})])        
        self.addOutputs([('NodeSocketShader', {'name':'Tangent'})])
        self.addLinks([('nodes["Geometry"].outputs[1]', 'nodes["CoTangent"].inputs[0]'),
            ('nodes["Tangent"].outputs[0]', 'nodes["CoTangent"].inputs[1]'),
            ('nodes["Geometry"].outputs[1]', 'nodes["ZDot"].inputs[1]'),
            ('nodes["CoTangent"].outputs[0]', 'nodes["YDot"].inputs[1]'),
            ('nodes["Tangent"].outputs[0]', 'nodes["XDot"].inputs[1]'),
            ('nodes["XDot"].outputs[1]', 'nodes["Combine XYZ"].inputs[0]'),
            ('nodes["YDot"].outputs[1]', 'nodes["Combine XYZ"].inputs[1]'),
            ('nodes["ZDot"].outputs[1]', 'nodes["Combine XYZ"].inputs[2]'),
            ('nodes["Combine XYZ"].outputs[0]', 'nodes["Scale"].inputs[1]'),
            ('nodes["Scale"].outputs[0]', 'nodes["Translate"].inputs[1]'),
            ('nodes["Translate"].outputs[0]', 'nodes["Group Output"].inputs[0]'),
            ('inputs[0]', 'nodes["XDot"].inputs[0]'),
            ('inputs[0]', 'nodes["YDot"].inputs[0]'),
            ('inputs[0]', 'nodes["ZDot"].inputs[0]'),
            ('nodes["Translate"].outputs[0]', 'nodes["Invert"].inputs[1]'),
            ('nodes["Invert"].outputs[0]', 'nodes["Negative"].inputs[0]'),
            ('nodes["Translate"].outputs[0]', 'nodes["Positive"].inputs[0]'),
            ('nodes["Positive"].outputs[0]', 'nodes["FinalCombine"].inputs[0]'),
            ('nodes["Positive"].outputs[1]', 'nodes["FinalCombine"].inputs[1]'),
            ('nodes["Positive"].outputs[2]', 'nodes["FinalCombine"].inputs[2]'),
            ('nodes["FinalCombine"].outputs[0]', 'nodes["EmiClosure"].inputs[0]'),
            ('nodes["EmiClosure"].outputs[0]', 'outputs[0]')])

    def copy(self, node):
        self.node_tree=node.node_tree.copy()
    
    def free(self):
        bpy.data.node_groups.remove(self.node_tree)
        
    def draw_buttons(self, context, layout):
        row=layout.row(align=True)
        row.alert=(self.axis_X.lstrip('-')==self.axis_Y.lstrip('-') or self.axis_X.lstrip('-')==self.axis_Z.lstrip('-'))
        row.prop(self, 'axis_X', text='')  
        row.alert=(self.axis_Y.lstrip('-')==self.axis_X.lstrip('-') or self.axis_Y.lstrip('-')==self.axis_Z.lstrip('-'))
        row.prop(self, 'axis_Y', text='')
        row.alert=(self.axis_Z.lstrip('-')==self.axis_X.lstrip('-') or self.axis_Z.lstrip('-')==self.axis_Y.lstrip('-'))
        row.prop(self, 'axis_Z', text='')
        row=layout.row()
        row.prop_search(self, "uvmap", context.active_object.data, "uv_layers", icon='GROUP_UVS')

    def draw_menu():
        return 'SH_NEW_BakeTools' , 'Bake Nodes'    
