#A wrapper class for python-magic.
import magic
import collections
from pprint import pprint

class cbmagic(magic.Magic):
    def __init__(self):
        magic.Magic.__init__(self)
        self.file_types=collections.OrderedDict()
        self.file_types['JPEG'] = 'jpg'
        self.file_types['PNG'] = 'png'
        self.file_types['PDF'] = 'pdf'
    def from_file(self, file):
        result=magic.Magic.from_file(self,file)
        #Return the file type: jpg, png or pdf                                                                                                                  
        return self.file_types[result.split(' ',1)[0]]

if __name__ == "__main__":
    from cb_idcheck import cbmagic
    myMagic = cbmagic.cbmagic()
    print("Deduces the file type from the file header and returns one of the following strings: 'jpg', 'png' or 'pdf'.")
    filename = input("File name: ")
    pprint(myMagic.from_file(filename))

