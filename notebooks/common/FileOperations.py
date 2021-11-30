import json

class FileOperations:

    def openFile(self,path):

        f = open(path,'r')
        return f

    def readData(self,f):

        txtFile = f.read()
        return txtFile

    def convertJson(self,txtFile):

        return eval(txtFile)

    def jsonLoad(self,path):

        with open(path) as data_file:
            data = json.load(data_file)

        return data

    def writeTxtFile(self,txt,outputFile):

        file = open(outputFile,'w')
        file.write(txt)
        file.close()