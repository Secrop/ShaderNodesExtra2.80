
#
#   Node Authors: nudelZ, Secrop
#
#   Node Description: Utility node for baking various Displacement maps
#
#   version: (0,1,1)
#

import bpy
from ShaderNodeBase import ShaderNodeCompact

class ShaderNodeDisplacementBake(ShaderNodeCompact):
    
    bl_name='ShaderNodeDisplacementBake'
    bl_label='Displacement Bake'
    bl_icon='NONE'
    
    axis_items=(('X', 'X', 'POS_X'),
            ('-X', '-X', 'NEG_X'),
            ('Y', 'Y', 'POS_Y'),
            ('-Y', '-Y', 'NEG_Y'),
            ('Z', 'Z', 'POS_Z'),
            ('-Z', '-Z', 'NEG_Z'))
    
    display_items=(('xyz','xyz', 'xyz'),('fas', 'fas', 'fas'))
    
    output_items=(('0','Position','Position'),('1','Scalar Displacement','Scalar Displacement'), ('2','Object Vector Displacement','World Displacement'), ('3','Tangent Vector Displacement','Tangent Displacement'))
    
    def enumupdate(self,context):
        def filteraxis(axis):
            if axis=='X':
                if int((self.zenum-1)%2)==1:
                    axis = '-' + axis
            elif axis=='Y':
                if int((self.zenum-1)/4%2)==1:
                    axis = '-' + axis
            elif axis=='Z':
                if int((self.zenum-1)/2%2)==1:
                    axis = '-' + axis
            return axis    
        axis_order=(('Y','Z','X'),('Z','Y','X'),('Y','X','Z'),('X','Y','Z'),('Z','X','Y'),('X','Z','Y'))
        seq=axis_order[int(self.zenum/8%6)]
        self.axis_X=filteraxis(seq[0])
        self.axis_Y=filteraxis(seq[1])
        self.axis_Z=filteraxis(seq[2])
           
    def axisupdate(self, context):
        if (self.axis_X.lstrip('-')==self.axis_Y.lstrip('-')) or (self.axis_X.lstrip('-')==self.axis_Z.lstrip('-')) or (self.axis_Y.lstrip('-')==self.axis_Z.lstrip('-')):
            return
        for i, cmp in enumerate([self.axis_X, self.axis_Y, self.axis_Z]):
            if self.outvalue=='2':
                fromsocket=self.node_tree.nodes["WorldSep"].outputs[i]
            elif self.outvalue=='3':    
                fromsocket=self.node_tree.nodes[cmp.lstrip('-')+'Dot'].outputs[1]
            tosocket=self.node_tree.nodes['Combine XYZ'].inputs[i]
            if tosocket.is_linked:
                self.node_tree.links.remove(tosocket.links[0])
            self.node_tree.links.new(fromsocket, tosocket)
            if cmp.startswith('-'):
                self.node_tree.nodes['FlipArray'].inputs[i].default_value=-1
            else:
                self.node_tree.nodes['FlipArray'].inputs[i].default_value=1

    def uvmapupdate(self, context):
        self.node_tree.nodes['Tangent'].uv_map=self.uvmap
    
    def outputupdate(self, context):
        nexit=self.node_tree.nodes["Emission"]
        if nexit.inputs[0].is_linked:
            self.node_tree.links.remove(nexit.inputs[0].links[0])
        if nexit.inputs[1].is_linked:
            self.node_tree.links.remove(nexit.inputs[1].links[0])
        
        if self.outvalue=='0':
            if self.inputs[0].is_linked:
                context.space_data.edit_tree.links.remove(self.inputs[0].links[0])
            if self.inputs[1].is_linked:
                context.space_data.edit_tree.links.remove(self.inputs[1].links[0])
            self.inputs[0].hide=True
            self.inputs[1].hide=True
            position=self.node_tree.nodes['Coordinates'].outputs[3]
            self.node_tree.links.new(position, nexit.inputs[0])
            nexit.inputs[1].default_value=1
        else:
            self.inputs[0].hide=False
            self.inputs[1].hide=False
            if self.outvalue=='1':
                input=self.node_tree.nodes['YDot'].outputs[1]
            else:
                input=self.node_tree.nodes['Multiply'].outputs[0]
                self.axisupdate(context)
            self.node_tree.links.new(input , nexit.inputs[0])                
            self.node_tree.links.new(self.node_tree.nodes['Group Input'].outputs[1], nexit.inputs[1])


    axis_X = bpy.props.EnumProperty(default = 'X', items = axis_items, name = "X_list", update = axisupdate)
    axis_Y = bpy.props.EnumProperty(default = 'Y',items = axis_items, name = "Y_list", update = axisupdate)
    axis_Z = bpy.props.EnumProperty(default = 'Z',items = axis_items, name = "Z_list", update = axisupdate)                                                 
    zenum = bpy.props.IntProperty(default = 25, name = 'FlipAndSwitch', min = 1, max = 48, update = enumupdate)
    uvmap = bpy.props.StringProperty(name = 'UV Map',default = '', update = uvmapupdate)
    display = bpy.props.EnumProperty(default = 'FlipAndSwitch' , items = (('XYZ','XYZ', 'Custom XYZ'),('FlipAndSwitch', 'ZBrush', 'Zbrush Compatible'))) # to be added : , ('Presets', 'Presets', 'Presets')
    outvalue = bpy.props.EnumProperty(default = '0' , items = output_items, name = 'Output', update=outputupdate)
    
    def init(self, context):
        self.width = 200
        self.node_tree = bpy.data.node_groups.new(self.bl_name+'nodetree', 'ShaderNodeTree')
        self.node_tree.is_hidden=True
        self.addNodes([('NodeGroupInput', {'name':'Group Input'}),
            ('NodeGroupOutput', {'name':'Group Output'}),
            ('ShaderNodeEmission', {'name':'Emission'}),
            ('ShaderNodeTexCoord', {'name':'Coordinates'}),
            ('ShaderNodeTangent', {'name':'Tangent', 'direction_type':'UV_MAP'}),
            ('ShaderNodeVectorMath', {'name':'SubPosition', 'operation':'SUBTRACT'}),
            ('ShaderNodeSeparateXYZ', {'name':'WorldSep'}),
            ('ShaderNodeVectorMath', {'name':'XDot', 'operation':'DOT_PRODUCT'}),
            ('ShaderNodeVectorMath', {'name':'ZDot', 'operation':'DOT_PRODUCT'}),
            ('ShaderNodeVectorMath', {'name':'YDot', 'operation':'DOT_PRODUCT'}),
            ('ShaderNodeVectorMath', {'name':'Vector Math', 'operation':'CROSS_PRODUCT'}),
            ('ShaderNodeCombineXYZ', {'name':'Combine XYZ'}),
            ('ShaderNodeMixRGB', {'name':'Multiply', 'blend_type':'MULTIPLY', 'use_clamp':False, 'inputs[0].default_value':1.0}),
            ('ShaderNodeCombineXYZ', {'name':'FlipArray', 'inputs[0].default_value':1.0, 'inputs[1].default_value':1.0, 'inputs[2].default_value':1.0})])
        self.addInputs([('NodeSocketVector', {'name':'Position (High Resolution)', 'hide_value':True, 'hide':True}),
            ('NodeSocketFloat', {'name':'Scale', 'default_value':1.0, 'min_value':0.0, 'max_value':10.0, 'hide':True})])
        self.addOutputs([('NodeSocketShader', {'name':'Vector'})])
        self.addLinks([('nodes["Vector Math"].outputs[0]', 'nodes["ZDot"].inputs[1]'),
            ('inputs[0]', 'nodes["SubPosition"].inputs[0]'),
            ('nodes["Coordinates"].outputs[3]', 'nodes["Emission"].inputs[0]'),
            ('nodes["Emission"].outputs[0]', 'outputs[0]'),
            ('nodes["Coordinates"].outputs[3]', 'nodes["SubPosition"].inputs[1]'),
            ('nodes["Coordinates"].outputs[1]', 'nodes["Vector Math"].inputs[0]'),
            ('nodes["Coordinates"].outputs[1]', 'nodes["YDot"].inputs[1]'),
            ('nodes["Tangent"].outputs[0]', 'nodes["XDot"].inputs[1]'),
            ('nodes["Tangent"].outputs[0]', 'nodes["Vector Math"].inputs[1]'),
            ('nodes["SubPosition"].outputs[0]', 'nodes["XDot"].inputs[0]'),
            ('nodes["SubPosition"].outputs[0]', 'nodes["YDot"].inputs[0]'),
            ('nodes["SubPosition"].outputs[0]', 'nodes["ZDot"].inputs[0]'),
            ('nodes["SubPosition"].outputs[0]', 'nodes["WorldSep"].inputs[0]'),
            ('nodes["FlipArray"].outputs[0]', 'nodes["Multiply"].inputs[1]'),
            ('nodes["Combine XYZ"].outputs[0]', 'nodes["Multiply"].inputs[2]'),
            ('nodes["XDot"].outputs[1]', 'nodes["Combine XYZ"].inputs[0]'),
            ('nodes["YDot"].outputs[1]', 'nodes["Combine XYZ"].inputs[1]'),
            ('nodes["ZDot"].outputs[1]', 'nodes["Combine XYZ"].inputs[2]')])

    def draw_buttons(self, context, layout):
        layout.prop(self, 'outvalue', text='')
        if self.outvalue=='2':
            row=layout.row(align=True)
            row.alert=(self.axis_X.lstrip('-')==self.axis_Y.lstrip('-') or self.axis_X.lstrip('-')==self.axis_Z.lstrip('-'))
            row.prop(self, 'axis_X', text='')  
            row.alert=(self.axis_Y.lstrip('-')==self.axis_X.lstrip('-') or self.axis_Y.lstrip('-')==self.axis_Z.lstrip('-'))
            row.prop(self, 'axis_Y', text='')
            row.alert=(self.axis_Z.lstrip('-')==self.axis_X.lstrip('-') or self.axis_Z.lstrip('-')==self.axis_Y.lstrip('-'))
            row.prop(self, 'axis_Z', text='')
        elif self.outvalue=='3':
            if self.display=='FlipAndSwitch':
                row=layout.row()
                row.prop(self, 'zenum', text='FlipAndSwitch:')
            elif self.display=='XYZ':
                row=layout.row(align=True)
                row.alert=(self.axis_X.lstrip('-')==self.axis_Y.lstrip('-') or self.axis_X.lstrip('-')==self.axis_Z.lstrip('-'))
                row.prop(self, 'axis_X', text='')  
                row.alert=(self.axis_Y.lstrip('-')==self.axis_X.lstrip('-') or self.axis_Y.lstrip('-')==self.axis_Z.lstrip('-'))
                row.prop(self, 'axis_Y', text='')
                row.alert=(self.axis_Z.lstrip('-')==self.axis_X.lstrip('-') or self.axis_Z.lstrip('-')==self.axis_Y.lstrip('-'))
                row.prop(self, 'axis_Z', text='')
            row=layout.row()
            row.prop_search(self, "uvmap", context.active_object.data, "uv_layers", icon='GROUP_UVS')        

    def draw_buttons_ext(self, context, layout):
        if self.outvalue=='3':
            layout.prop(self, 'display', text='Interface:')
            
    def copy(self, node):
        self.node_tree=node.node_tree.copy()      
     
    def free(self):
        bpy.data.node_groups.remove(self.node_tree)    

    def draw_menu():
        return 'SH_NEW_BakeTools' , 'Bake Nodes'
