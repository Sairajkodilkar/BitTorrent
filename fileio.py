import errno
import stat
import os


class File:

    flags = {
        "+": os.O_RDWR,
        "r": os.O_RDONLY,
        "w": os.O_WRONLY,
        "c": os.O_CREAT
    }

    permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH

    def __init__(self, file_name, mode):
        flag = 0
        for i in mode:
            flag |= self.flags[i]
        self._fd = os.open(file_name, flag, self.permissions)
        return

    def write(self, byte_str):
        return os.write(self._fd, byte_str)

    def read(self, n):
        return os.read(self._fd, n)

    def seek(self, pos, how):
        return os.lseek(self._fd, pos, how)

    def close(self):
        return os.close(self._fd)


class FileArray:

    def __init__(self, files, piece_length):
        self.file_streams  = []
        self.total_size    = 0
        self._piece_length = piece_length
        self._create_directory_structure(files)
        self._open_files(files)

    @property
    def piece_length(self):
        return self._piece_length

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
        self.total_size = 0
        for file_name, file_length in files:
            self.total_size += file_length
            file_stream = File(file_name, "+c")
            self.file_streams.append((file_stream, file_length))
        return

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
        if(block == None):
            return
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
        # get the offset of the block within the first file
        block_start = (self._piece_length * index) + begin
        file_start = 0
        for file, file_length in self.file_streams:
            file_end = file_start + file_length
            if(block_start >= file_start and block_start < file_end):
                return block_start - file_start
            file_start = file_end
        return -1

    def get_block_files(self, index, begin, length):
        # get the file streams associated with the block
        block_start = (self._piece_length * index) + begin
        block_end = block_start + length
        file_start = 0
        add_files = False
        files = []

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

    def close_all(self):
        for file_stream, file_length in self.file_streams:
            file_stream.close()
        return
