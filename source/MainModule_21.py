import re
import itertools
import numpy as np
import csv
import os


gerber2meshFile = "mesh.msh"
patternFile= "temp.out"
MaterialFile = "material.txt"
ParametersFile = "InputParameters.csv"
materialCsvFile = r"Material.csv"

outputFile = r"logfile.out"

n_LINES = 3

""" Npy Binary Files """
FR4PROPSFile = "FR4PROPS"
CuPROPSFile = "CuPROPS"
materialMatrixFile = "materialmatrixfile"

"""Dirs"""
currentDir = os.path.dirname(os.path.abspath(__file__))
MaterialFileDir = currentDir + "\\"+ MaterialFile
InputParametersDir = currentDir + "\\" + ParametersFile
gerberFileDir = currentDir+ "\\" + gerber2meshFile
materialCsvFileDir = currentDir + "\\" + materialCsvFile

outputFileDir = currentDir + "\\" + outputFile
#binary files dirs
FR4PROPSFileDir = currentDir + "\\" + FR4PROPSFile +".npy"
CuPROPSFileDir = currentDir + "\\" + CuPROPSFile +".npy"
materialMatrixFileDir = currentDir + "\\" + materialMatrixFile + ".npy"


def readGerber2MeshFile(gerber2meshFile, patternFile, MaterialFile, n_LINES):
    data = open(gerber2meshFile).read()
    start_end_re = re.compile("^gerber2mesh(.*?)\nEnd Data$", re.I|re.M|re.S)
    matches = start_end_re.findall(data)


    with open(patternFile,"w") as fp:
        for item in matches:
            fp.write(item)
            fp.write("\n")
            fp.write("-"*40)
    fp.close()
    with open(patternFile) as f:
        with open(MaterialFile, "w+") as fm:
            for line in itertools.islice(f, n_LINES, None):
                fm.write(line)
    f.close()
    fm.close()
    return
    
def converTxtIntoCSV(txtFile, outcsvFile):
    
    txtFile = csv.reader(open(txtFile, "rb"), delimiter = '\t')
    outcsvFile = csv.writer(open(outcsvFile, 'wb'))
    outcsvFile.writerows(txtFile)
    return

def createMaterialPropsMatrix(fileCsv):
    materialMatrix = np.genfromtxt(fileCsv, delimiter=',',
                      usecols=(1,2,3,4,5,6,7,8,9,10), skip_footer=1)
    return materialMatrix
            
def readInputMaterial(fileCsv, skipHeaderLines, skipFooterLines):
    MProps = np.genfromtxt(fileCsv, delimiter=';',
                     usecols=(1,2,3,4,5), skip_header=skipHeaderLines, 
                     skip_footer=skipFooterLines)

    return MProps 

def getElementProps(materialInMatrix, element):
    row = materialInMatrix[np.nonzero(materialInMatrix == element) [0],:]
    return row
  
def createOutputFile(FR4PROPS, CuPROPS , ElemProps, ElemOut):
    with open(outputFileDir, 'w') as f:
        f.write("This are the Fr4 Properties\n")
        f.write(" ".join(map(str, FR4PROPS)))
        f.write("\n")
        f.write("This are the Cu4 Properties\n")
        f.write(" ".join(map(str, CuPROPS)))
        f.write("\n")
        f.write("This are the Element properties which we are using\n")
        f.write(" ".join(map(str, ElemProps)))
        f.write("\n")
        f.write("This are the Element Homogenized properties\n")
        f.write(" ".join(map(str, ElemOut)))
        f.write("\n")
        
        f.close()
    return
    
    
if __name__ == "__main__":
    
    try:
        if(os.path.isfile(MaterialFileDir) == True 
                                & os.path.isfile(InputParametersDir)== True):
            pass
    
    except Exception, e:
        print e, ":File does not exist, aborting"

    
    if(os.path.isfile(gerberFileDir) == True & os.path.isfile(materialCsvFileDir)):
        pass
    else:
        readGerber2MeshFile(gerber2meshFile, patternFile, MaterialFile, n_LINES)
        converTxtIntoCSV(MaterialFile,materialCsvFile)


  
    if(os.path.isfile(materialMatrixFileDir) == True):
        
        materialMatrix = np.load(materialMatrixFile + ".npy")
        pass
    
    else:
        materialMatrix = createMaterialPropsMatrix(materialCsvFile)
        np.save(materialMatrixFile, materialMatrix)
    
    
    
    if(os.path.isfile(FR4PROPSFileDir) == True 
                    & os.path.isfile(CuPROPSFileDir) == True  ):
        FR4PROPS = np.load(FR4PROPSFile + ".npy")
        CuPROPS = np.load(CuPROPSFile + ".npy")
        pass
    else:
        FR4PROPS = readInputMaterial(ParametersFile,1, 17)
        CuPROPS = readInputMaterial(ParametersFile,18, 0)
        np.save(FR4PROPSFile, FR4PROPS)
        np.save(CuPROPSFile, CuPROPS)
    
    
    seekelem = 503822.0
    ElemProps = getElementProps(materialMatrix, seekelem)
    
    HomoG = ElemProps * 2
#     print FR4PROPS.shape
#     print CuPROPS.shape
#     print ElemProps.shape
    
    createOutputFile(FR4PROPS[0,:], CuPROPS[0,:], ElemProps[:], HomoG)

    