from pysam import AlignmentFile as SamFile
import gzip


def remove_ext(filename, extensions):
    ext = filename.split('.')[-1]
    if ext in extensions:
        without_ext = '.'.join(filename.split('.')[:-1])
        return remove_ext(without_ext, extensions)
    else:
        return filename


def iter_chunks(handle, n, preprocess=lambda x: x):
    chunk = [None] * n
    for j, line in enumerate(handle):
        i = j % n
        if (i == 0) and (j != 0):
            yield chunk
            chunk = [None] * n
        chunk[i] = preprocess(line)
    yield chunk


def open_maybe_gzip(filename):
    if type(filename) == str:
        handle = open(filename)
    else:
        handle = filename
        filename = handle.name        
    if '.gz' in filename:
        handle = gzip.open(handle.buffer, mode='rt')
    return handle


def open_samfile(handle):
    ext = 'r'
    if '.bam' in handle.name:
        ext = 'rb'
    samfile = SamFile(handle, ext)
    return samfile


def parse_bed_file(bed_file):
    out = {}
    for line in bed_file:
        tkns = line.split()
        region = (int(tkns[1]), int(tkns[2]))
        try:
            out[tkns[0]].append(region)
        except KeyError:
            out[tkns[0]] = [region]
        except IndexError:
            continue
    return out


def get_bc_token(id_line):
    tkns = id_line.split()
    for tkn in tkns:
        if 'BX:' in tkn:
            return tkn


def get_bc_sam(read):
    return 'BX:Z:' + read.get_tag('BX') + ',BC:Z:' + read.get_tag('BC')


def get_read_id(id_line):
    tkns = id_line.split()
    return tkns[0][1:]


def parse_bc_map(filename):
    bc_map = {}
    handle = open_maybe_gzip(filename)
    for chunk in iter_chunks(handle, 4):
        rid = get_read_id(chunk[0])
        bc = get_bc_token(chunk[0])
        bc_map[rid] = bc
    handle.close()
    return bc_map


def parse_bc_list(handle):
    return {bc.strip() for bc in handle}
