'''
6:string
i3e l4:spam3:egge
d3:cowi3ee
'''

import struct
import sys

class BencodingError(Exception):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BdecodingError(Exception):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Token:

    INT_TYPE = b'i'
    STRING_TYPE = b's'
    DICT_TYPE  = b'd'
    LIST_TYPE = b'l'
    END_TYPE = b'e'
    EOF_TYPE = b'f'

    def __init__(self, value, ttype):
        self.value = value
        self.type = ttype
        pass

class Bdecoder:

    def __init__(self, encoding, typeof):
        if(typeof != "f" and typeof != "b"):
            raise BdecodingError("Wrong Encoding object type")
        if(typeof == "f"):
            self.encoding = open(encoding, "rb")
        else:
            self.encoding = encoding
        self.typeof = typeof
        self.stringpointer = 0

    def decode(self)->list:
        bdecodingList = []
        while True:
            token = self.getnext()
            if(token.type == Token.EOF_TYPE):
                break
            else:
                bdecodingList.append(token.value)
        return bdecodingList

    def getnbytes(self, n):
        if(self.typeof == "f"):
            return self.encoding.read(n)
        else:
            nbytes = self.encoding[self.stringpointer:self.stringpointer + n]
            self.stringpointer += n
            return nbytes

    def getnext(self):
            ch = self.getnbytes(1)
            if(ch >= b'0' and ch <= b'9'):
                digits = ch.decode()
                while(True):
                    ch = self.getnbytes(1)
                    if(ch == b':'):
                        break
                    elif(not (ch >= b'0' and ch <= b'9')):
                        raise BdecodingError("Expected Digit got {}".format(ch))
                    digits += ch.decode()
                strlen = int(digits)
                string = self.readstring(strlen)
                return Token(string, Token.STRING_TYPE)
            elif(ch == Token.INT_TYPE):
                integer = self.readinteger()
                return Token(integer, Token.INT_TYPE)
            elif(ch == Token.LIST_TYPE):
                ll = self.readlist()
                return Token(ll, Token.LIST_TYPE)
            elif(ch == Token.DICT_TYPE):
                dictionary = self.readdictionary()
                return Token(dictionary, Token.DICT_TYPE)
            elif(ch == Token.END_TYPE):
                return Token(None, Token.END_TYPE)
            elif(not ch):
                return Token(None, Token.EOF_TYPE)
            else:
                raise BdecodingError(f"Unexpected Type specifier: {ord(ch)}")

    def readstring(self, strlen):
        if(strlen < 0):
            return ''
        string = self.getnbytes(strlen)
        if(len(string) != strlen):
            raise BdecodingError("Bad String Encoding")
        return string
    
    def readinteger(self):
        integerString = ''
        start = True
        zeroFlag = False
        while(True):
            ch = self.getnbytes(1)
            if(ch == b'e'):
                if(start):
                    raise BdecodingError("Empty integer in bencoding")
                else:
                    break
            elif(not ch):
                raise BdecodingError("Unexpected EOF")
            elif(not (ch >= b'0' and ch <= b'9') and not (start and ch == b'-')):
                raise BdecodingError("Unexpected character")
            elif(zeroFlag):
                raise BdecodingError("Cannot have a digit after 0")
            if(ch == b'0' and start):
                zeroFlag = True
            start = False
            integerString += ch.decode()
        return int(integerString) 

    def readdictionary(self):
        dictionary = {}
        while(True):
            key = self.getnext()
            if(key.type == Token.EOF_TYPE):
                raise BdecodingError("Unexpected EOF")
            if(key.type == Token.END_TYPE):
                break
            value = self.getnext()
            if(key.type == Token.END_TYPE):
                raise BdecodingError("Dictionary Cannot have Empty value field")
            dictionary[key.value] = value.value
        return dictionary

    def readlist(self):
        elementlist = []
        while(True):
            element = self.getnext()
            if(element.type == Token.EOF_TYPE):
                raise BdecodingError("Unexpected EOF")
            if(element.type == Token.END_TYPE):
                break
            elementlist.append(element.value)
        return elementlist

class Bencoder:
    
    def bencode(self, value):
        bencoding = None
        if(isinstance(value, bytes)):
            bencoding = self.bencodestr(value)
        elif(isinstance(value, int)):
            bencoding = self.bencodeint(value)
        elif(isinstance(value, list)):
            bencoding = self.bencodelist(value)
        elif(isinstance(value, dict)):
            bencoding = self.bencodedict(value)
        else:
            raise BencodingError("Bad Object Type")
        return bencoding
            
    def bencodestr(self, value):
        if(not isinstance(value, bytes)):
            raise BencodingError("Bad Object Type")
        bencoding = str(len(value)).encode()
        bencoding += ":".encode() + value
        return bencoding

    def bencodeint(self, value):
        if(not isinstance(value, int)):
            raise BencodingError("Bad Object Type")
        bencoding = Token.INT_TYPE
        bencoding += str(value).encode()
        bencoding += Token.END_TYPE
        return bencoding

    def bencodedict(self, value):
        if(not isinstance(value, dict)):
            raise BencodingError("Bad Object Type")
        bencoding = Token.DICT_TYPE
        for k, v in value.items():
            bencoding += self.bencode(k)
            bencoding += self.bencode(v)
        bencoding += Token.END_TYPE
        return bencoding

    def bencodelist(self, value):
        if(not isinstance(value, list)):
            raise BencodingError("Bad Object Type")
        bencoding = Token.LIST_TYPE
        for i in value:
            bencoding += self.bencode(i)
        bencoding += Token.END_TYPE
        return bencoding




