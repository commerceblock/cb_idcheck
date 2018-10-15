#A wrapper class for python-magic.
import magic

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

def test_cbmagic():
    myMagic = cbmagic()
    pprint(myMagic.from_file('/Users/lawrence/Projects/ocean-idcheck/testPicture.png'))
    pprint(myMagic.from_file('/Users/lawrence/Projects/ocean-idcheck/testPicture.jpg'))
    pprint(myMagic.from_file('/Users/lawrence/Projects/ocean-idcheck/onfidoTerms.pdf'))
