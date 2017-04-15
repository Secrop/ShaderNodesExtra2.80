import bpy

class ShaderNodeBase(bpy.types.NodeCustomGroup):
      
    def __path_resolve__(self, obj, path):
        if "." in path:
            extrapath, path= path.rsplit(".", 1)
            obj = obj.path_resolve(extrapath)
        return obj, path
            
    def value_get(self, obj, path):         
        obj, path=self.__path_resolve__(obj, path)
        return getattr(obj, path)                
    
    def value_set(self, obj, path, val):
        obj, path=self.__path_resolve__(obj, path)
        setattr(obj, path, val)                
    
    def setupTree(self, unique=False):
        name=self.bl_name + '_nodetree'
        if unique or bpy.data.node_groups.find(name)==-1:
            self.node_tree=bpy.data.node_groups.new(name + '_nodetree', 'ShaderNodeTree')
            self.addNode('NodeGroupInput', {'name':'Group Input'})
            self.addNode('NodeGroupOutput', {'name':'Group Output'})
            if hasattr(self.node_tree, 'is_hidden'):
                self.node_tree.is_hidden=True
            if hasattr(self, 'defaultNodeTree'):
                self.defaultNodeTree()
            elif hasattr(self, 'defaultNodeScript'):
                import ShadeNodeScript
                ShaderNodeScript.compile(self, name)    
            else:
                print('No default NodeTree found')
        else:
            self.node_tree=bpy.data.node_groups[name]
        self.nodes=self.node_tree.nodes
        self.links=self.node_tree.links

    def addNode(self, nodetype, attrs):
        node=self.node_tree.nodes.new(nodetype)
        for attr in attrs:
            self.value_set(node, attr, attrs[attr])
        return node
        
    def delNode(self, node):
        if isinstance(node, str):
            node=self.node_tree.path_resolve(node)
        self.node_tree.nodes.remove(node)
    
    def addLink(self, socketFrom, socketTo):
        if isinstance(socketFrom, str):
            if socketFrom.startswith('inputs'):
                socketFrom=self.node_tree.path_resolve('nodes["Group Input"].outputs' + socketFrom[socketFrom.rindex('['):])
            else:
                socketFrom=self.node_tree.path_resolve(socketFrom)
        if isinstance(socketTo, str):
            if socketTo.startswith('outputs'):
                socketTo=self.node_tree.path_resolve('nodes["Group Output"].inputs' + socketTo[socketTo.rindex('['):])
            else:
                socketTo=self.node_tree.path_resolve(socketTo)
        self.node_tree.links.new(socketFrom, socketTo)
    
    def delLink(self, link):
        if isinstance(link, str):
            link=self.node_tree.path_resolve(link)
        self.node_tree.links.remove(link)

    def addInput(self, sockettype, attrs):
        name = attrs.pop('name')
        socketInterface=self.node_tree.inputs.new(sockettype, name)
        socket=self.path_resolve(socketInterface.path_from_id())
        for attr in attrs:
            if attr in ['default_value', 'hide', 'hide_value']:
                self.value_set(socket, attr, attrs[attr])
            else:
                self.value_set(socketInterface, attr, attrs[attr])
        return socket
        
    def delInput(self, socket):
        if isinstance(socket, str):
            socket=self.node_tree.path_resolve(socket)
        self.node_tree.inputs.remove(socket)
    
    def addOutput(self, sockettype, attrs):
        name = attrs.pop('name')
        socketInterface=self.node_tree.outputs.new(sockettype, name)
        socket=self.path_resolve(socketInterface.path_from_id())
        for attr in attrs:
            if attr in ['default_value']:
                self.value_set(socket, attr, attrs[attr])
            else:
                self.value_set(socketInterface, attr, attrs[attr])
        return socket
        
    def delOutput(self, socket):
        if isinstance(socket, str):
            socket=self.node_tree.path_resolve(socket)
        self.node_tree.outputs.remove(socket)
    
    def category(self):
        return 'Extra Nodes'
    