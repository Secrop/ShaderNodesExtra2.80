import bpy

class ShaderNodeBase():

    def value_set(self, obj, path, value):
        if "." in path:
            path_prop, path_attr = path.rsplit(".", 1)
            prop = obj.path_resolve(path_prop)
        else:
            prop = obj
            path_attr = path
        setattr(prop, path_attr, value)

    def getNodetree(self):
        name=self.bl_name + '_nodetree'
        if bpy.data.node_groups.find(name)==-1:
            self.defaultNodetree(name)
        else:
            self.node_tree=bpy.data.node_groups[name]
            
    def socket_path_resolve(self, socket, attr):
        if attr in ['default_value', 'hide', 'hide_value']:
            path=socket
        else:
            path='node_tree.' + socket
        return self.path_resolve(path)                    

    def addSocket(self, is_output, sockettype, attrs):
        if 'name' in attrs.keys():
            name=attrs.pop('name')
        else:
            return
        if is_output==True:
            socket=self.node_tree.outputs.new(sockettype, name)
            for attr in attrs:
                self.value_set(self.socket_path_resolve(socket.path_from_id(), attr), attr, attrs[attr])
        elif is_output==False:
            socket=self.node_tree.inputs.new(sockettype, name)
            for attr in attrs:
               self.value_set(self.socket_path_resolve(socket.path_from_id(), attr), attr, attrs[attr])
        return socket
    
    def getSocket(self, is_output, socketname):
        if is_output==True:
            Sockets=self.node_tree.nodes['Group Output'].inputs
        elif is_output==False:
            Sockets=self.node_tree.nodes['Group Input'].outputs
        if Sockets.find(socketname)>-1:
            return Sockets[socketname]    
        return None
        
    def defaultNodetree(self, name):    
        raise AttributeError('Method "defaultNodetree(self, name)" must be defined')

    def addNode(self, nodetype, attrs):
        node=self.node_tree.nodes.new(nodetype)
        for attr in attrs:
            self.value_set(node, attr, attrs[attr])
        return node
    
    def getNode(self, nodename):
        if self.node_tree.nodes.find(nodename)>-1:
            return self.node_tree.nodes[nodename]
        return None
    
    def innerLink(self, socketin, socketout):
        SI=self.node_tree.path_resolve(socketin)
        SO=self.node_tree.path_resolve(socketout)
        self.node_tree.links.new(SI, SO)
   
    #This must go evenfurther
    def is_extLinked(self, socket):
        result=False
        if socket.is_linked:
			#If the node is inside a node_group we probably need to probe the bpy.context
            if socket.links[0].from_node.type=='REROUTE':
                result=self.is_extLinked(socket.links[0].from_node.inputs[0])
            else:
                result=True
        return result

    def free(self):
        if self.node_tree.users==1:
            bpy.data.node_groups.remove(self.node_tree, do_unlink=True)


