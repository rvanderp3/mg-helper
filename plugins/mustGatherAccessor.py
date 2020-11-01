import yaml
import os.path
from os import path
import tarfile

class MustGatherAccessor:
    tarcache = None
    tar = None
    name = "must-gather accessor"
    def __init__ (self,filename):        
        self.filename = filename
        
    def readfile(self):
        if path.isdir(self.filename):
            pass
        else:
            try:
                # attempt to load a tar.gz file
                self.tar = tarfile.open(self.filename,"r:gz")
                
            except ValueError:
                try:
                    self.tar = tarfile.open(self.filename,"r")
                except ValueError:
                    raise
            self.buildTarCache(self.tar)

    def buildTarCache(self,tar):
        self.tarcache = {}
        for member in tar.getmembers():
            if member.isfile() != True:
                continue

            # sanitize the paths - this will make a life a little easier for our plugins
            splits = member.name.split("/")
            if splits[0].startswith("must-gather"):
                splits.remove(splits[0]) 
                first=True
                member.name=""
                for part in splits:
                    if first:
                        first = False
                    else:
                        member.name+="/"
                    member.name+=part
            self.tarcache[member.name] = member

    def getValueFromObj(self,obj,*props):
        if obj != None:
            for prop in props:                        
                if prop in obj:
                    obj = obj[prop]
                else:
                    obj = None
                    break
        return obj
        
    def getFileContent(self,thepath):
        
        content = None
        if self.tarcache == None:
            if path.exists(thepath):
                f = open(thepath,"r")
                content = f.read()
        else:
            f=self.tar.extractfile(thepath)            
            content = f.read()
        return content

    def getEntriesFromPath(self,path):
        entries = []
        if self.tarcache != None:
            for key in self.tarcache:        
                if path in key:
                    entries.append(key)
        else:
            fullPath = os.path.join(self.filename,path)
            if os.path.exists(fullPath):
                pathsEntries = os.listdir(fullPath)
                for entry in pathsEntries:
                    foundPath = os.path.join(fullPath,entry)
                    if(os.path.isfile(foundPath)):
                        entries.append(foundPath)
        return entries
    def getDirsFromPath(self,path):
        entries = []
        if self.tarcache != None:
            for key in self.tarcache:        
                if path in key:
                    entries.append(key)
        else:
            fullPath = os.path.join(self.filename,path)
            if os.path.exists(fullPath):
                pathsEntries = os.listdir(fullPath)
                for entry in pathsEntries:
                    foundPath = os.path.join(fullPath,entry)
                    if(os.path.isdir(foundPath)):
                        entries.append(foundPath)
        return entries

    def parseYaml(self, content):
        return yaml.safe_load(content)

    
