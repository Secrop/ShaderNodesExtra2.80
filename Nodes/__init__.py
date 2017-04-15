<<<<<<< HEAD
import os

ignore_list=['__init__.py', 'ShaderNodeBase.py'] 
def listNodes():
    nodelist=[]
    for subdir, dirs, files in os.walk(os.path.dirname(__file__)):
        current_dir = os.path.basename(subdir)
        if current_dir == '__pycache__':
            continue
        for file in files:
            if file in ignore_list:
                continue
            if not file.endswith('.py'):
                continue
            nodelist.append(file[:-3])
    return nodelist
=======
import os

ignore_list=['__init__.py', 'ShaderNodeBase.py'] 
def listNodes():
    nodelist=[]
    for subdir, dirs, files in os.walk(os.path.dirname(__file__)):
        current_dir = os.path.basename(subdir)
        if current_dir == '__pycache__':
            continue
        for file in files:
            if file in ignore_list:
                continue
            if not file.endswith('.py'):
                continue
            nodelist.append(file[:-3])
    return nodelist
>>>>>>> master
