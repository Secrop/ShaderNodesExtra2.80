
#
#   Node Authors: Secrop
#
#   Node Description: Interpolation Node
#
#   version: (0,1,1)
#

import bpy
from ShaderNodeBase import ShaderNodeCompact

class ShaderNodeInterpolate(ShaderNodeCompact):

    bl_name='ShaderNodeInterpolate'
    bl_label='Interpolate'
    bl_icon='NONE'
    
    interpolation_list=[('LIN', 'Lerp', 'Lerp'),
                        ('SMTS', 'SmoothStep', 'SmoothStep'),
                        ('SMTRS', 'SmootherStep', 'SmootherStep'),
                        ('HP', 'HighPower', 'HighPower'),
                        ('IHP', 'Invert HighPower', 'InvHighPower'),
                        ('SIN', 'Sine', 'Sine'),
                        ('ISIN', 'Invert Sine', 'InvSine'),
                        ('COS', 'Cos', 'CosPi'),
                        ('CTMR', 'Catmull-Rom', 'Catmull-Rom')]
    
    def interpol_update(self, context):
        out=self.node_tree.nodes['MIXENTRY'].inputs[0]
        if out.is_linked:
            self.node_tree.links.remove(out.links[0])
        self.inputs[1].enabled=False
        self.inputs[2].enabled=False
        self.inputs[3].enabled=False
        if self.interpolation=='LIN':
            src='inputs[0]'
        elif self.interpolation=='SMTS':
            src='nodes["SmoothStep"].outputs[0]'
        elif self.interpolation=='SMTRS':
            src='nodes["SmootherStep"].outputs[0]'
        elif self.interpolation=='HP':
            self.inputs[1].enabled=True
            src='nodes["HighPower"].outputs[0]'
        elif self.interpolation=='IHP':
            self.inputs[1].enabled=True
            src='nodes["InvHighPower"].outputs[0]'
        elif self.interpolation=='SIN':
            src='nodes["Sin"].outputs[0]'
        elif self.interpolation=='ISIN':
            src='nodes["InvSin"].outputs[0]'
        elif self.interpolation=='COS':
            src='nodes["Cos"].outputs[0]'
        elif self.interpolation=='CTMR':
            self.inputs[2].enabled=True
            self.inputs[3].enabled=True
            src='nodes["CATMULLROM"].outputs[0]'
        self.addLinks([(src, out)])    
    
    
    interpolation: bpy.props.EnumProperty(name='interpolation', items=interpolation_list, default='LIN', update=interpol_update)                    


    def init(self, context):
        ntname = '.' + self.bl_name + '_nodetree'
        self.node_tree=bpy.data.node_groups.new(ntname, 'ShaderNodeTree')
        self.addNodes([('NodeGroupInput', {'name':'Group Input'}),
            ('NodeGroupOutput', {'name':'Group Output'}),
            ('ShaderNodeMath', {'name':'CAT01', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':1.0}),
            ('ShaderNodeMath', {'name':'CAT03', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':2.0}),
            ('ShaderNodeMath', {'name':'CAT04', 'operation':'ADD', 'use_clamp':0.0, 'inputs[1].default_value':4.0}),
            ('ShaderNodeMath', {'name':'CAT05', 'operation':'SUBTRACT', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'CAT07', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'CAT09', 'operation':'SUBTRACT', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'CAT10', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[1].default_value':3.0}),
            ('ShaderNodeMath', {'name':'CAT12', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'CAT08', 'operation':'ADD', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'CAT13', 'operation':'ADD', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'CATMULLROM', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':0.5}),
            ('ShaderNodeMath', {'name':'IS02', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':1.571}),
            ('ShaderNodeMath', {'name':'IS03', 'operation':'SINE', 'use_clamp':0.0, 'inputs[1].default_value':1.571}),
            ('ShaderNodeMath', {'name':'InvSin', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':1.0}),
            ('ShaderNodeMath', {'name':'Sin', 'operation':'SINE', 'use_clamp':0.0, 'inputs[1].default_value':0.5}),
            ('ShaderNodeMath', {'name':'IHP2', 'operation':'POWER', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'InvHighPower', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':1.0}),
            ('ShaderNodeMath', {'name':'SMM03', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':6.0}),
            ('ShaderNodeMath', {'name':'SMM04', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[1].default_value':15.0}),
            ('ShaderNodeMath', {'name':'SMM05', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'SMM06', 'operation':'ADD', 'use_clamp':0.0, 'inputs[1].default_value':10.0}),
            ('ShaderNodeMath', {'name':'SM03', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':3.0}),
            ('ShaderNodeMath', {'name':'SM02', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':2.0}),
            ('ShaderNodeMath', {'name':'HighPower', 'operation':'POWER', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'IHP01', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':1.0}),
            ('ShaderNodeMath', {'name':'S01', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':1.571}),
            ('ShaderNodeMath', {'name':'IS01', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':1.0}),
            ('ShaderNodeMath', {'name':'CAT02', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'SmoothStep', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'SmootherStep', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'VPOW3', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'VPOW2', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'C03', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':0.5}),
            ('ShaderNodeMath', {'name':'Cos', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':0.5}),
            ('ShaderNodeMath', {'name':'C02', 'operation':'COSINE', 'use_clamp':0.0, 'inputs[1].default_value':0.5}),
            ('ShaderNodeMath', {'name':'C01', 'operation':'MULTIPLY', 'use_clamp':0.0, 'inputs[1].default_value':-3.142}),
            ('ShaderNodeMath', {'name':'MIX01', 'operation':'SUBTRACT', 'use_clamp':0.0, 'inputs[0].default_value':1.0}),
            ('NodeReroute', {'name':'MIXENTRY'}),
            ('ShaderNodeMath', {'name':'MIX02', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'MIX03', 'operation':'MULTIPLY', 'use_clamp':0.0}),
            ('ShaderNodeMath', {'name':'MIX04', 'operation':'ADD', 'use_clamp':0.0})])
        self.addInputs([('NodeSocketFloat', {'name':'Fac', 'default_value':0.0, 'min_value':0.0, 'max_value':1.0}),
            ('NodeSocketFloat', {'name':'Power', 'default_value':2.0, 'min_value':1.0, 'enabled':False}),
            ('NodeSocketFloat', {'name':'Catmull1', 'default_value':0.0, 'enabled':False}),
            ('NodeSocketFloat', {'name':'Catmull2', 'default_value':1.0, 'enabled':False}),
            ('NodeSocketFloat', {'name':'Value1', 'default_value':0.0}),
            ('NodeSocketFloat', {'name':'Value2', 'default_value':1.0})])
        self.addOutputs([('NodeSocketFloat', {'name':'Value'})])
        self.addLinks([('nodes["MIX01"].outputs[0]', 'nodes["MIX03"].inputs[0]'),
            ('nodes["MIX03"].outputs[0]', 'nodes["MIX04"].inputs[0]'),
            ('nodes["MIX02"].outputs[0]', 'nodes["MIX04"].inputs[1]'),
            ('nodes["MIXENTRY"].outputs[0]', 'nodes["MIX01"].inputs[1]'),
            ('nodes["MIXENTRY"].outputs[0]', 'nodes["MIX02"].inputs[0]'),
            ('nodes["SM02"].outputs[0]', 'nodes["SM03"].inputs[1]'),
            ('nodes["VPOW2"].outputs[0]', 'nodes["SmoothStep"].inputs[1]'),
            ('nodes["MIX04"].outputs[0]', 'outputs[0]'),
            ('nodes["SMM04"].outputs[0]', 'nodes["SMM05"].inputs[1]'),
            ('nodes["VPOW3"].outputs[0]', 'nodes["SmootherStep"].inputs[1]'),
            ('nodes["SMM03"].outputs[0]', 'nodes["SMM04"].inputs[0]'),
            ('nodes["SMM05"].outputs[0]', 'nodes["SMM06"].inputs[0]'),
            ('nodes["IHP01"].outputs[0]', 'nodes["IHP2"].inputs[0]'),
            ('nodes["IHP2"].outputs[0]', 'nodes["InvHighPower"].inputs[1]'),
            ('nodes["S01"].outputs[0]', 'nodes["Sin"].inputs[0]'),
            ('nodes["IS02"].outputs[0]', 'nodes["IS03"].inputs[0]'),
            ('nodes["IS01"].outputs[0]', 'nodes["IS02"].inputs[0]'),
            ('nodes["IS03"].outputs[0]', 'nodes["InvSin"].inputs[1]'),
            ('nodes["C01"].outputs[0]', 'nodes["C02"].inputs[0]'),
            ('nodes["C02"].outputs[0]', 'nodes["C03"].inputs[0]'),
            ('nodes["C03"].outputs[0]', 'nodes["Cos"].inputs[1]'),
            ('nodes["CAT01"].outputs[0]', 'nodes["CAT02"].inputs[1]'),
            ('nodes["CAT04"].outputs[0]', 'nodes["CAT05"].inputs[0]'),
            ('nodes["CAT07"].outputs[0]', 'nodes["CAT08"].inputs[1]'),
            ('nodes["CAT08"].outputs[0]', 'nodes["CAT13"].inputs[0]'),
            ('nodes["CAT12"].outputs[0]', 'nodes["CAT13"].inputs[1]'),
            ('nodes["CAT13"].outputs[0]', 'nodes["CATMULLROM"].inputs[0]'),
            ('nodes["CAT05"].outputs[0]', 'nodes["CAT07"].inputs[1]'),
            ('nodes["CAT02"].outputs[0]', 'nodes["CAT08"].inputs[0]'),
            ('nodes["CAT03"].outputs[0]', 'nodes["CAT04"].inputs[0]'),
            ('nodes["CAT09"].outputs[0]', 'nodes["CAT10"].inputs[0]'),
            ('nodes["CAT10"].outputs[0]', 'nodes["CAT12"].inputs[1]'),
            ('inputs[1]', 'nodes["HighPower"].inputs[1]'),
            ('inputs[1]', 'nodes["IHP2"].inputs[1]'),
            ('inputs[2]', 'nodes["CAT01"].inputs[1]'),
            ('inputs[2]', 'nodes["CAT03"].inputs[0]'),
            ('inputs[2]', 'nodes["CAT09"].inputs[1]'),
            ('inputs[3]', 'nodes["CAT05"].inputs[1]'),
            ('inputs[3]', 'nodes["CAT09"].inputs[0]'),
            ('inputs[4]', 'nodes["MIX03"].inputs[1]'),
            ('inputs[5]', 'nodes["MIX02"].inputs[1]'),
            ('inputs[0]', 'nodes["VPOW2"].inputs[0]'),
            ('inputs[0]', 'nodes["VPOW2"].inputs[1]'),
            ('inputs[0]', 'nodes["SM02"].inputs[0]'),
            ('nodes["VPOW2"].outputs[0]', 'nodes["VPOW3"].inputs[0]'),
            ('inputs[0]', 'nodes["VPOW3"].inputs[1]'),
            ('inputs[0]', 'nodes["SMM05"].inputs[0]'),
            ('inputs[0]', 'nodes["SMM03"].inputs[0]'),
            ('inputs[0]', 'nodes["HighPower"].inputs[0]'),
            ('inputs[0]', 'nodes["IHP01"].inputs[1]'),
            ('inputs[0]', 'nodes["S01"].inputs[0]'),
            ('inputs[0]', 'nodes["IS01"].inputs[1]'),
            ('inputs[0]', 'nodes["C01"].inputs[0]'),
            ('inputs[0]', 'nodes["CAT02"].inputs[0]'),
            ('nodes["VPOW2"].outputs[0]', 'nodes["CAT07"].inputs[0]'),
            ('nodes["VPOW3"].outputs[0]', 'nodes["CAT12"].inputs[0]'),
            ('nodes["SM03"].outputs[0]', 'nodes["SmoothStep"].inputs[0]'),
            ('nodes["SMM06"].outputs[0]', 'nodes["SmootherStep"].inputs[0]'),
            ('inputs[0]', 'nodes["MIXENTRY"].inputs[0]')])

    def copy(self, node):
        self.node_tree=node.node_tree.copy()      
     
    def free(self):
        bpy.data.node_groups.remove(self.node_tree, do_unlink=True)  

    def draw_buttons(self, context, layout):
        layout.prop(self, "interpolation", text='')
    
    def draw_label(self):
        idx=self.bl_rna.properties['interpolation'].enum_items.find(self.interpolation)
        return self.bl_rna.properties['interpolation'].enum_items[idx].name
        
    def draw_menu():
        return 'SH_NEW_CONVERTOR' , 'Converter'    

