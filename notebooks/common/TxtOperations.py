class TxtOperations:

    def divideTxt(self,txt,separator):

        return txt.split(separator)

    def getParameters(self,fileOperations,pathFile):

        txtOperations = TxtOperations()
        parametersValuesFile = fileOperations.openFile(pathFile)
        values = fileOperations.readData(parametersValuesFile)
        valuesMatrix = txtOperations.divideTxt(values, '\n')
        listParametersValues = {}

        for valueMatrix in valuesMatrix:
            key = valueMatrix.split('=')[0]
            value = valueMatrix.split('=')[1]
            listParametersValues[key] = value

        return listParametersValues