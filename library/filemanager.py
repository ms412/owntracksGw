import os
import glob
import time

class filemanager(object):

    def __init__(self):
        self._path = None
        self._extendsion = '*'
        self._filelist = []
        self._content = {}
        self._modTime = 0

    def _getFilelist(self):
        return glob.glob(os.path.join(self._path,self._extendsion))

    def setPath(self,path):
        self._path = path
        return True

    def setExtendsion(self,extendsion):
        self._extendsion = extendsion
     #   print(self._extendsion,extendsion)
        return True

    def filelist(self):
       # self._filelist = glob.glob(os.path.join(self._path,self._extendsion))
        self._filelist=self._getFilelist()
        return self._filelist

    def changes(self):
        print('Ext',self._extendsion)
        #_tempfilelist = glob.glob(os.path.join(self._path,self._extendsion))
        _tempFileList = self._getFilelist()
        print('1',self._filelist)
        print('2',_tempFileList)
        _diff =  set(_tempFileList).symmetric_difference(set(self._filelist))
        self._filelist = _tempFileList
        print('DIFF',_diff)

        return _diff

    def modified(self):
        _modifiedFiles = []
        _tempFileList = self._getFilelist()
    #    print('filelist',_tempFileList)
     #   print('modtime',self._modTime)
        for file in _tempFileList:
            _modTime = os.path.getmtime(file)
      #      print('modtime',_modTime,'file',file)
            if self._modTime < _modTime:
       #         print('modified file',file)
                _modifiedFiles.append(file)

        self._modTime = time.time()
        return _modifiedFiles
       # os.path.getmtime(path)

    def createFile(self,filename):
        filepath = os.path.join(self._path, filename)
        f = open(filepath, "a")
        f.close()
    # with open(self._filename,'w')as fh:



if __name__ == '__main__':
    _f = filemanager()
    _f.setPath('C:/Users/tgdscm41/PycharmProjects/onwtracksGW/cards')
   # _f.changes()
    _f.setExtendsion('*.json')
    print('1',_f.modified())
   # print(_f.filelist())
    time.sleep(3)
    _f.createFile('xx.json')
    print('2',_f.modified())
    _f.createFile('xx.a')
    print('3', _f.modified())
   # _f.changes()
#    _f.path('../cards')
 #   print(_f.filelist())