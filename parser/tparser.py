'''
6:string
i3e
l4:spam3:egge
d3:cowi3ee
'''

class Token:

    INT_TYPE = 'i'
    STRING_TYPE = 's'
    DICT_TYPE  = 'd'
    LIST_TYPE = 'l'
    END_TYPE = 'e'
    EOF_TYPE = 'f'

    def __init__(self, value, ttype):
        self.token = value
        self.type = ttype
        pass

class TorrentParser:
    def parser(self, filename)->list:
        '''
        States:
            1) specifier
            2) and element
        Functions:
            1) parse dictionary
            2) parse list
            3) parse string
            4) parse integer
        '''
        '''
        call get next in the will loop 
        get next will get the next token
        depending on the next token call 
                read string, 
                read readdictionary,
                readlist,
                readinteger
        '''

    def getnext(self, file):
            '''
            read character 
            if(integer): read till ":" and then readstring
            if(i): readinteger till e
            if(l): readlist
            if(d): readdictionary
            if(e): e
            '''
            ch = file.read(1)
            if(ch.isdigit()):
                digits = ch
                while(True):
                    ch = file.read(1)
                    if(ch == ':'):
                        break
                    elif(not ch.isdigit()):
                        raise BencodingError("Expected Digit got {}".format(ch))
                    digits += ch
                strlen = int(digits)
                string = self.readstring(file, strlen)
                return Token(string, Token.STRING_TYPE)

            elif(ch == 'i'):
                integer = self.readinteger(file)
                return Token(integer, Token.INT_TYPE)
            elif(ch == 'l'):
                ll = self.readlist(file)
                return Token(ll, Token.LIST_TYPE)
            elif(ch == 'd'):
                dictionary = self.readdictionary(file)
                return Token(dictionary, Token.DICT_TYPE)
            elif(ch == 'e'):
                return Token(None, Token.END_TYPE)


    def readstring(self, file, strlen):
        if(strlen < 0):
            return ''
        string = file.read(strlen)
        if(len(string) != strlne):
            raise BencodingError("Bad String Encoding")
    
    def readinteger(self, file):
        integerString = ''
        start = True
        while(True):
            ch = file.read(1)
            if(ch == 'e'):
                if(start):
                    raise BencodingError("Empty integer in bencoding")
                else:
                    break
            elif(not ch):
                raise BencodingError("Unexpected EOF")
            elif(not ch.isdigit() and not (start and ch == '-')):
                raise BencodingError("Unexpected character")
            elif(zeroFlag):
                raise BencodingError("Cannot have a digit after 0")
            if(ch == '0' and start):
                zeroFlag = True
            start = False
            integerString += ch

        return int(integerString) 


    def readdictionary(self, file):
        dictionary = {}

        while(True):
            key = self.getnext(file)
            if(key.type == token.EOF_TYPE):
                raise BencodingError("Unexpected EOF")
            if(key.type == Token.END_TYPE):
                break
            value = self.getnext(file)
            if(key.type == Token.END_TYPE):
                raise BencodingError("Dictionary Cannot have Empty value field")
            dictionary[key.value] = value.value

        return dictionary

    def readlist(self, file):
        elementlist = []
        while(True):
            element = self.getnext(file)
            if(element.type == Token.EOF_TYPE):
                raise BencodingError("Unexpected EOF")
            if(element.type == Token.END_TYPE):
                break
            elementlist.append(element.value)

        return elementlist
