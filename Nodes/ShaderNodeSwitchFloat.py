
#
#   Node Authors: Secrop
#
#   Node Description: Switch Node
#
#   version: (0,1,1)
#

import bpy
from ShaderNodeBase import ShaderNodeCompact

class ShaderNodeSwitchFloat(ShaderNodeCompact):

    bl_name='ShaderNodeSwitchFloat'
    bl_label='Switch Float'
    bl_icon='NONE'

    def init(self, context):
        ntname= '.' + self.bl_name + '_nodetree'
        if bpy.data.node_groups.find(ntname)>-1:
            self.node_tree=bpy.data.node_groups[ntname]
        else:    
            self.node_tree=bpy.data.node_groups.new(ntname, 'ShaderNodeTree')
            self.addNodes([('NodeGroupInput', {'name':'Group Input'}),
                ('NodeGroupOutput', {'name':'Group Output'}),
                ('ShaderNodeMath', {'name':'Math', 'operation':'GREATER_THAN', 'use_clamp':0.0, 'inputs[1].default_value':0.0}),
                ('ShaderNodeMath', {'name':'Math.002', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':1.0}),
                ('ShaderNodeMath', {'name':'Math.003', 'operation':'MULTIPLY', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Math.001', 'operation':'MULTIPLY', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Math.004', 'operation':'ADD', 'use_clamp':0.0})])
            self.addInputs([('NodeSocketInt', {'name':'Switch', 'default_value':0, 'min_value':0, 'max_value':1}),
                ('NodeSocketFloat', {'name':'Value1', 'default_value':0.5, 'min_value':-10000.0, 'max_value':10000.0}),
                ('NodeSocketFloat', {'name':'Value2', 'default_value':0.5, 'min_value':-10000.0, 'max_value':10000.0})])
            self.addOutputs([('NodeSocketFloat', {'name':'Value'})])
            self.addLinks([('nodes["Math"].outputs[0]', 'nodes["Math.001"].inputs[0]'),
                ('nodes["Math"].outputs[0]', 'nodes["Math.002"].inputs[1]'),
                ('nodes["Math.002"].outputs[0]', 'nodes["Math.003"].inputs[0]'),
                ('nodes["Math.003"].outputs[0]', 'nodes["Math.004"].inputs[0]'),
                ('nodes["Math.001"].outputs[0]', 'nodes["Math.004"].inputs[1]'),
                ('nodes["Group Input"].outputs[0]', 'nodes["Math"].inputs[0]'),
                ('nodes["Group Input"].outputs[1]', 'nodes["Math.003"].inputs[1]'),
                ('nodes["Group Input"].outputs[2]', 'nodes["Math.001"].inputs[1]'),
                ('nodes["Math.004"].outputs[0]', 'nodes["Group Output"].inputs[0]')])

    def free(self):
        if self.node_tree.users==1:
            bpy.data.node_groups.remove(self.node_tree, do_unlink=True)
            
    def draw_menu():
        return 'SH_NEW_CONVERTOR' , 'Converter'
