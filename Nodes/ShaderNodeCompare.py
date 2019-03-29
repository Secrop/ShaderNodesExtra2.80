
#
#   Node Authors: Secrop
#
#   Node Description: Compare Node
#
#   version: (0,1,2)
#

import bpy
from ShaderNodeBase import ShaderNodeCompact

class ShaderNodeCompare(ShaderNodeCompact):

    bl_name='ShaderNodeCompare'
    bl_label='Compare'
    bl_icon='NONE'
                        
    def init(self, context):
        name = '.' + self.bl_name + '_nodetree'
        if bpy.data.node_groups.find(name)>-1:
            self.node_tree=bpy.data.node_groups[name]
            for ind in [0,2,3,4,5]:
                self.outputs[ind].enabled=False
        else:    
            self.node_tree=bpy.data.node_groups.new(name, 'ShaderNodeTree')
            self.addNodes([('NodeGroupInput', {'name':'Group Input'}),
                ('NodeGroupOutput', {'name':'Group Output'}),
                ('ShaderNodeMath', {'name':'Math.002', 'operation':'MAXIMUM', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Greater', 'operation':'GREATER_THAN', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Equal', 'operation':'LESS_THAN', 'use_clamp':0.0, 'inputs[1].default_value':0.500}),
                ('ShaderNodeMath', {'name':'GreaterEqual', 'operation':'MAXIMUM', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'LessEqual', 'operation':'MAXIMUM', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Less', 'operation':'LESS_THAN', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'NotEqual', 'operation':'GREATER_THAN', 'use_clamp':0.0, 'inputs[1].default_value':0.500}),
                ('ShaderNodeMath', {'name':'Sim01', 'operation':'SUBTRACT', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Sim02', 'operation':'ABSOLUTE', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Similar', 'operation':'LESS_THAN', 'use_clamp':0.0}),])
            self.addInputs([('NodeSocketFloat', {'name':'Threshold', 'default_value':0.500, 'min_value':0.0, 'max_value':10000.0, 'enabled':False}),
                ('NodeSocketFloat', {'name':'A', 'default_value':0.500, 'min_value':-10000.0, 'max_value':10000.0}),
                ('NodeSocketFloat', {'name':'B', 'default_value':0.500, 'min_value':-10000.0, 'max_value':10000.0})])
            self.addOutputs([('NodeSocketInt', {'name':'Value', 'enabled':False}),
                ('NodeSocketInt', {'name':'Value', 'enabled':False}),
                ('NodeSocketInt', {'name':'Value'}),
                ('NodeSocketInt', {'name':'Value', 'enabled':False}),
                ('NodeSocketInt', {'name':'Value', 'enabled':False}),
                ('NodeSocketInt', {'name':'Value', 'enabled':False}),
                ('NodeSocketInt', {'name':'Value', 'enabled':False})])
            self.addLinks([('inputs[0]', 'nodes["Similar"].inputs[1]'),
                ('inputs[1]', 'nodes["Greater"].inputs[0]'),
                ('inputs[2]', 'nodes["Greater"].inputs[1]'),
                ('inputs[1]', 'nodes["Less"].inputs[0]'),
                ('inputs[2]', 'nodes["Less"].inputs[1]'),
                ('inputs[1]', 'nodes["Sim01"].inputs[0]'),
                ('inputs[2]', 'nodes["Sim01"].inputs[1]'),
                ('nodes["Greater"].outputs[0]', 'outputs[0]'),
                ('nodes["Less"].outputs[0]', 'outputs[4]'),
                ('nodes["Greater"].outputs[0]', 'nodes["Math.002"].inputs[0]'),
                ('nodes["Less"].outputs[0]', 'nodes["Math.002"].inputs[1]'),
                ('nodes["Math.002"].outputs[0]', 'nodes["NotEqual"].inputs[0]'),
                ('nodes["Equal"].outputs[0]', 'outputs[2]'),
                ('nodes["Math.002"].outputs[0]', 'nodes["Equal"].inputs[0]'),
                ('nodes["Greater"].outputs[0]', 'nodes["GreateEqual"].inputs[0]'),
                ('nodes["Equal"].outputs[0]', 'nodes["GreateEqual"].inputs[1]'),
                ('nodes["GreateEqual"].outputs[0]', 'outputs[1]'),
                ('nodes["Equal"].outputs[0]', 'nodes["LessEqual"].inputs[0]'),
                ('nodes["Less"].outputs[0]', 'nodes["LessEqual"].inputs[1]'),
                ('nodes["LessEqual"].outputs[0]', 'outputs[3]'),
                ('nodes["NotEqual"].outputs[0]', 'outputs[5]'),
                ('nodes["Sim01"].outputs[0]', 'nodes["Sim02"].inputs[0]'),
                ('nodes["Sim02"].outputs[0]', 'nodes["Similar"].inputs[0]'),
                ('nodes["Similar"].outputs[0]', 'outputs[6]')])

    def ops_update(self, context):
        outs=[]
        if self.operation=='Similar To':
            self.inputs[0].enabled=True
        else:
            self.inputs[0].enabled=False  
        for i in self.outputs:
            if i.is_linked:
                for link in i.links:
                    outs.append(link.to_socket)
                    context.space_data.edit_tree.links.remove(link)
            i.enabled=False
        ind=self.bl_rna.properties['operation'].enum_items.find(self.operation)               
        self.outputs[ind].enabled=True
        for ln in outs:
            context.space_data.edit_tree.links.new(self.outputs[ind], ln)


    ops_items=[('Greater Than', 'Greater Than', 'Greater Than'), ('Greater Than or Equal To', 'Greater Than or Equal To', 'Greater Than or Equal To'), ('Equal To', 'Equal To', 'Equal To'), ('Less Than or Equal To', 'Less Than or Equal To', 'Less Than or Equal To'), ('Less Than', 'Less Than', 'Less Than'), ('Not Equal To', 'Not Equal To', 'Not Equal To'), ('Similar To', 'Similar To', 'Similar To')]
    operation: bpy.props.EnumProperty(default = 'Equal To', items = ops_items, name = "Operation", update = ops_update)

    def free(self):
        if self.node_tree.users==1:
            bpy.data.node_groups.remove(self.node_tree, do_unlink=True)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'operation', text='')
        
    def draw_label(self):
        idx=self.bl_rna.properties['operation'].enum_items.find(self.operation)
        return self.bl_rna.properties['operation'].enum_items[idx].name
        
    def draw_menu():
        return 'SH_NEW_CONVERTOR' , 'Converter'
