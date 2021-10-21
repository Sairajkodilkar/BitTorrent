class Files:

    def __init__(self, directory:bool, name:str, files=None, basedir=None):
        #files only in case if it is directory
        self.directory = directory
        self.name = name
        self.files = files
        '''
        create the directory/file here with name name
        in case of directory open all files 
        create the dict of the files and corrosponding boundries
        '''
        pass

    def write_piece(self, piece, index, begin, length):
        '''
        Write the piece to the file
        while writing the piece take care of the boundaries
        '''
        pass

    def read_piece(self, index, begin, length):
        '''
        read the piece from the file/s
        determine the piece boundries
        '''
        return piece

    def get_file_name(self, index, begin, length):
        ''' return list of files which is the piece is covering
        determine it using the dict of filenames and there length 
        '''

    def break_piece(piece, length):
        '''
        break piece in the corrosponding length piece
        '''
        pass

