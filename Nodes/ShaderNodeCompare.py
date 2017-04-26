import bpy

class ShaderNodeCompare(bpy.types.NodeCustomGroup):

    bl_name='ShaderNodeCompare'
    bl_label='Compare'
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
                    self.value_set(socketInterface, attr, inputitem[1][attr])
            
    def addOutputs(self, outputs):
        for outputitem in outputs:
            name = outputitem[1].pop('name')
            socketInterface=self.node_tree.outputs.new(outputitem[0], name)
            socket=self.path_resolve(socketInterface.path_from_id())
            for attr in outputitem[1]:
                if attr in ['default_value', 'hide', 'hide_value']:
                    self.value_set(socket, attr, outputitem[1][attr])
                else:
                    self.value_set(socketInterface, attr, outputitem[1][attr])
                    
    def init(self, context):
        name=self.bl_name + '_nodetree'
        if bpy.data.node_groups.find(name)>-1:
            self.node_tree=bpy.data.node_groups[name]
        else:    
            self.node_tree=bpy.data.node_groups.new(name, 'ShaderNodeTree')
            if hasattr(self.node_tree, 'is_hidden'):
                self.node_tree.is_hidden=True
            self.addNodes([('NodeGroupInput', {'name':'Group Input'}),
                ('NodeGroupOutput', {'name':'Group Output'}),
                ('ShaderNodeMath', {'name':'Math.002', 'operation':'MAXIMUM', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Greater', 'operation':'GREATER_THAN', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Equal', 'operation':'LESS_THAN', 'use_clamp':0.0, 'inputs[1].default_value':0.500}),
                ('ShaderNodeMath', {'name':'GreateEqual', 'operation':'MAXIMUM', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'LessEqual', 'operation':'MAXIMUM', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'Less', 'operation':'LESS_THAN', 'use_clamp':0.0}),
                ('ShaderNodeMath', {'name':'NotEqual', 'operation':'GREATER_THAN', 'use_clamp':0.0, 'inputs[1].default_value':0.500})])
            self.addInputs([('NodeSocketFloat', {'name':'A', 'default_value':0.500, 'min_value':-10000.0, 'max_value':10000.0}),
                ('NodeSocketFloat', {'name':'B', 'default_value':0.500, 'min_value':-10000.0, 'max_value':10000.0})])
            self.addOutputs([('NodeSocketFloat', {'name':'Value', 'hide':True}),
                ('NodeSocketFloat', {'name':'Value', 'hide':True}),
                ('NodeSocketFloat', {'name':'Value'}),
                ('NodeSocketFloat', {'name':'Value', 'hide':True}),
                ('NodeSocketFloat', {'name':'Value', 'hide':True}),
                ('NodeSocketFloat', {'name':'Value', 'hide':True})])
            self.addLinks([('nodes["Group Input"].outputs[0]', 'nodes["Greater"].inputs[0]'),
                ('nodes["Group Input"].outputs[1]', 'nodes["Greater"].inputs[1]'),
                ('nodes["Group Input"].outputs[0]', 'nodes["Less"].inputs[0]'),
                ('nodes["Group Input"].outputs[1]', 'nodes["Less"].inputs[1]'),
                ('nodes["Greater"].outputs[0]', 'nodes["Group Output"].inputs[0]'),
                ('nodes["Less"].outputs[0]', 'nodes["Group Output"].inputs[4]'),
                ('nodes["Greater"].outputs[0]', 'nodes["Math.002"].inputs[0]'),
                ('nodes["Less"].outputs[0]', 'nodes["Math.002"].inputs[1]'),
                ('nodes["Math.002"].outputs[0]', 'nodes["NotEqual"].inputs[0]'),
                ('nodes["Equal"].outputs[0]', 'nodes["Group Output"].inputs[2]'),
                ('nodes["Math.002"].outputs[0]', 'nodes["Equal"].inputs[0]'),
                ('nodes["Greater"].outputs[0]', 'nodes["GreateEqual"].inputs[0]'),
                ('nodes["Equal"].outputs[0]', 'nodes["GreateEqual"].inputs[1]'),
                ('nodes["GreateEqual"].outputs[0]', 'nodes["Group Output"].inputs[1]'),
                ('nodes["Equal"].outputs[0]', 'nodes["LessEqual"].inputs[0]'),
                ('nodes["Less"].outputs[0]', 'nodes["LessEqual"].inputs[1]'),
                ('nodes["LessEqual"].outputs[0]', 'nodes["Group Output"].inputs[3]'),
                ('nodes["NotEqual"].outputs[0]', 'nodes["Group Output"].inputs[5]')])

    def ops_update(self, context):
        outs=[]
        for i in self.outputs:
            if i.is_linked:
                for link in i.links:
                    outs.append(link.to_socket)
                    context.space_data.edit_tree.links.remove(link)
            i.hide=True
        ind=self.bl_rna.properties['ops_enum'].enum_items.find(self.ops_enum)               
        self.outputs[ind].hide=False
        for ln in outs:
            context.space_data.edit_tree.links.new(self.outputs[ind], ln)


    ops_items=[('Greater Than', 'Greater Than', 'Greater Than'), ('Greater Than or Equal To', 'Greater Than or Equal To', 'Greater Than or Equal To'), ('Equal To', 'Equal To', 'Equal To'), ('Less Than or Equal To', 'Less Than or Equal To', 'Less Than or Equal To'), ('Less Than', 'Less Than', 'Less Than'), ('Not Equal To', 'Not Equal To', 'Not Equal To')]
    ops_enum=bpy.props.EnumProperty(default = 'Equal To', items = ops_items, name = "Operation", update = ops_update)

        
    #def copy(self, node):

    def free(self):
        if self.node_tree.users==1:
            bpy.data.node_groups.remove(self.node_tree)
        
    #def socket_value_update(self, context):

    #def update(self):

    def draw_buttons(self, context, layout):
        layout.prop(self, 'ops_enum', text='')
        
    #def draw_buttons_ext(self, contex, layout):

    def draw_label(self):
        return self.ops_enum

    def draw_menu():
        return 'SH_NEW_CONVERTOR' , 'Converter'