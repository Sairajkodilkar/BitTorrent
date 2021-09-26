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

class TorrentParser:

    def parse(self, file)->list:
        bencodingList = []
        while True:
            token = self.getnext(file)
            if(token.type == Token.EOF_TYPE):
                break
            else:
                bencodingList.append(token.value)

        return bencodingList


    def getnext(self, file):
            ch = file.read(1)
            if(ch >= b'0' and ch <= b'9'):
                digits = ch.decode()
                while(True):
                    ch = file.read(1)
                    if(ch == b':'):
                        break
                    elif(not (ch >= b'0' and ch <= b'9')):
                        raise BencodingError("Expected Digit got {}".format(ch))
                    digits += ch.decode()
                strlen = int(digits)
                string = self.readstring(file, strlen)
                return Token(string, Token.STRING_TYPE)

            elif(ch == Token.INT_TYPE):
                integer = self.readinteger(file)
                return Token(integer, Token.INT_TYPE)
            elif(ch == Token.LIST_TYPE):
                ll = self.readlist(file)
                return Token(ll, Token.LIST_TYPE)
            elif(ch == Token.DICT_TYPE):
                dictionary = self.readdictionary(file)
                return Token(dictionary, Token.DICT_TYPE)
            elif(ch == Token.END_TYPE):
                return Token(None, Token.END_TYPE)
            elif(not ch):
                return Token(None, Token.EOF_TYPE)
            else:
                raise BencodingError(f"Unexpected Type specifier: {ord(ch)}")


    def readstring(self, file, strlen):
        if(strlen < 0):
            return ''
        string = file.read(strlen)
        if(len(string) != strlen):
            raise BencodingError("Bad String Encoding")
        return string
    
    def readinteger(self, file):
        integerString = ''
        start = True
        zeroFlag = False
        while(True):
            ch = file.read(1)
            if(ch == b'e'):
                if(start):
                    raise BencodingError("Empty integer in bencoding")
                else:
                    break
            elif(not ch):
                raise BencodingError("Unexpected EOF")
            elif(not (ch >= b'0' and ch <= b'9') and not (start and ch == b'-')):
                raise BencodingError("Unexpected character")
            elif(zeroFlag):
                raise BencodingError("Cannot have a digit after 0")
            if(ch == b'0' and start):
                zeroFlag = True
            start = False
            integerString += ch.decode()

        return int(integerString) 


    def readdictionary(self, file):
        dictionary = {}

        while(True):
            key = self.getnext(file)
            if(key.type == Token.EOF_TYPE):
                raise BencodingError("Unexpected EOF")
            if(key.type == Token.END_TYPE):
                break
            value = self.getnext(file)
            if(key.type == Token.END_TYPE):
                raise BencodingError("Dictionary Cannot have Empty value field")
            dictionary[key.value.decode()] = value.value

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
