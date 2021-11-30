:q
    import  os, sys

class WorkingDir:
    
    def getPath(self):
        sys.path.insert(1, os.path.join(sys.path[0], './'))
        return sys.path
    
