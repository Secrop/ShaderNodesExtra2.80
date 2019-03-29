
#
#   Node Authors: Secrop
#
#   Node Description: Node for creating loops over some nodegroup
#
#   version: (0,1,0)
#

import bpy

class ShaderNodeLoop(bpy.types.ShaderNodeCustomGroup):
    
    bl_name='ShaderNodeLoop'
    bl_label='Loop Node'
    
    def nodegroups(self, context):
        nt=context.space_data.edit_tree
        list=[('None','None','None')]
        for nd in nt.nodes:
            if nd.type=='GROUP':
                ng=nd.node_tree
                if ng.inputs.get('iterator'):
                    list.append((ng.name, ng.name, ng.name))
        return list            
      
    def __nodeinterface_setup__(self):
        self.node_tree.outputs.clear()
        self.node_tree.inputs.clear()
        if self.step_nodegroup=='None':
            return
        for input in bpy.data.node_groups[self.step_nodegroup].inputs:
            if not input.name=='iterator':
                self.node_tree.nodes['Group Input'].outputs.new(input.bl_socket_idname, input.name)
                self.node_tree.inputs.new(input.bl_socket_idname, input.name)
        for output in bpy.data.node_groups[self.step_nodegroup].outputs:
            self.node_tree.nodes['Group Output'].inputs.new(output.bl_socket_idname, output.name)
            self.node_tree.outputs.new(output.bl_socket_idname, output.name)
    
    def __nodetree_setup__(self):
        self.node_tree.links.clear()
        for node in self.node_tree.nodes:
            if not node.name in ['Group Input','Group Output']:
                self.node_tree.nodes.remove(node)
        if self.step_nodegroup=='None':
            return        
        previousnode=self.node_tree.nodes['Group Input']
        for iter in range(self.iterations):
            curnode=self.node_tree.nodes.new('ShaderNodeGroup')                    
            curnode.node_tree=bpy.data.node_groups[self.step_nodegroup]
            curnode.inputs['iterator'].default_value=iter            
            for input in curnode.inputs:
                poutput=previousnode.outputs.get(input.name)
                if poutput:
                    self.node_tree.links.new(poutput, input)
            if iter==self.iterations-1:
                for input in self.node_tree.nodes['Group Output'].inputs:
                    poutput=curnode.outputs.get(input.name)
                    if poutput:
                        self.node_tree.links.new(poutput, input)
            else:
                previousnode=curnode        

    def update_nt(self, context):
        self.__nodeinterface_setup__()
        self.__nodetree_setup__()
    
    def update_it(self, context):
        self.__nodetree_setup__()
                
    step_nodegroup: bpy.props.EnumProperty(name="step_nodegroup", items=nodegroups, update=update_nt)    
    
    iterations: bpy.props.IntProperty(name="iterations", min=1, max=63, default=8, update=update_it)
        
    
    def init(self, context):
        ntname = '.' + self.bl_name
        self.node_tree=bpy.data.node_groups.new(ntname, 'ShaderNodeTree')
        self.node_tree.nodes.new('NodeGroupInput')
        self.node_tree.nodes.new('NodeGroupOutput') 
    
    def draw_buttons(self, context, layout):
        row=layout.row()
        row.alert=(self.step_nodegroup=='None')
        row.prop(self, 'step_nodegroup', text='')
        row=layout.row()
        row.prop(self, 'iterations', text='iterations')
        
    def copy(self, node):
        self.node_tree=node.node_tree.copy()
    
    def free(self):
        bpy.data.node_groups.remove(self.node_tree, do_unlink=True)
