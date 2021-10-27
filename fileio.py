from bittorrent.piece import *
import os
import errno

class FileArray:

    #if files not none then name must belong to the directory
    def __init__(self, files, piece_length):

        self.piece_length = piece_length
        self.file_streams = []
        self._create_directory_structure(files)
        self._open_files(files)

    def _create_directory(self, dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:
            if(exc.errno != errno.EEXIST):
                raise
        return

    def _create_directory_structure(self, files):
        for file_name, file_length in files:
            file_dirname = os.path.dirname(file_name)
            if(file_dirname):
                self._create_nested_directory(file_dirname)
        return

    def _create_nested_directory(self, directory_path):
        directory_list = directory_path.split('/')
        directory_path = ''
        for directory in directory_list:
            self._create_directory(directory_path + directory)
            directory_path += directory + '/'
        return 
                
    def _open_files(self, files):
        for file_name, file_length in files:
            #TODO handle condition when file exists
            #In that case you have to verify the pieces in the files
            file_stream = open(file_name, "wb+")
            self.file_streams.append((file_stream, file_length))

    def read_block(self, index, begin, length):
        block = b''
        files = self.get_block_files(index, begin, length)
        offset = self.get_block_offset(index, begin)
        print(files)
        for file, file_length in files:
            file.seek(offset, 0)
            read_length = min(length, file_length - offset)
            print(read_length)
            block += file.read(read_length)
            print(block)
            length -= read_length
            offset = 0
        return block

    def write_block(self, index, begin, block):
        #write the piece to the file
        files = self.get_block_files(index, 0, len(block))
        offset = self.get_block_offset(index, 0)
        print(files, offset)
        start = 0
        for file, file_length in files:
            file.seek(offset, 0)
            file.write(block[start:start + file_length - offset])
            start += file_length - offset
            offset = 0
        return

    def get_block_offset(self, index, begin):
        #get the offset of the block within the first file
        piece_start = (self.piece_length * index) + begin
        file_start = 0
        for file, file_length in self.file_streams:
            file_end = file_start + file_length
            if(piece_start >= file_start and piece_start < file_end):
                return piece_start - file_start
        return -1

    def get_block_files(self, index, begin, length):
        #get the file streams associated with the block
        piece_start = (self.piece_length * index) + begin
        piece_end   = piece_start + length
        file_start  = 0
        add_files   = False
        files       = []

        for file_stream, file_length in self.file_streams:
            print(file_stream, file_length)
            file_end = file_start + file_length
            print(file_start, piece_start)
            print(piece_start >= file_start, piece_start < file_end)
            if(piece_start >= file_start and piece_start < file_end):
                print("this is true")
                add_files = True
            if(add_files):
                print("adding files")
                files.append((file_stream, file_length))
            if(piece_end >= file_start and piece_end < file_end):
                break
            file_start += file_length

        return files
    
        


