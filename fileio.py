from bittorrent.piece import *
import os
import errno

class File:

    flags = {
            "+":os.O_RDWR,
            "r":os.O_RDONLY,
            "w":os.O_WRONLY,
            "c":os.O_CREAT
        }

    def __init__(self, file_name, mode):
        flag = 0
        for i in mode:
            flag |= self.flags[i]
        self.fd = os.open(file_name, flag)

    def write(self, byte_str):
        return os.write(self.fd, byte_str)
    
    def read(self, n):
        return os.read(self.fd, n)

    def seek(self, pos, how):
        return os.lseek(self.fd, pos, how)

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
        #TODO handle condition when file exists
        #In that case you have to verify the pieces in the files
        for file_name, file_length in files:
            file_stream = File(file_name, "+c")
            self.file_streams.append((file_stream, file_length))

    def read_block(self, index, begin, length):
        block = b''
        files = self.get_block_files(index, begin, length)
        offset = self.get_block_offset(index, begin)
        for file, file_length in files:
            file.seek(offset, os.SEEK_SET)
            read_length = min(length, file_length - offset)
            block += file.read(read_length)
            length -= read_length
            offset = 0
        return block

    def write_block(self, index, begin, block):
        #write the piece to the file
        files = self.get_block_files(index, begin, len(block))
        offset = self.get_block_offset(index, begin)
        start = 0
        for file, file_length in files:
            file.seek(offset, os.SEEK_SET)
            file.write(block[start:start + file_length - offset])
            start += file_length - offset
            offset = 0
        return

    def get_block_offset(self, index, begin):
        #get the offset of the block within the first file
        block_start = (self.piece_length * index) + begin
        file_start = 0
        for file, file_length in self.file_streams:
            file_end = file_start + file_length
            if(block_start >= file_start and block_start < file_end):
                return block_start - file_start
            file_start = file_end
        return -1

    def get_block_files(self, index, begin, length):
        #get the file streams associated with the block
        block_start = (self.piece_length * index) + begin
        block_end   = block_start + length
        file_start  = 0
        add_files   = False
        files       = []

        for file_stream, file_length in self.file_streams:
            file_end = file_start + file_length
            if(block_start >= file_start and block_start < file_end):
                add_files = True
            if(add_files):
                files.append((file_stream, file_length))
            if(block_end >= file_start and block_end < file_end):
                break
            file_start += file_length

        return files
    
        


