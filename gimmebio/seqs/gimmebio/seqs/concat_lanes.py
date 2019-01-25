
import subprocess as sp
from sys import stdout
from os.path import basename


def getSname(fname):
    return fname.split('/')[-1].split('_L')[0]


def getLane(fname):
    return int(fname.split('/')[-1].split('L00')[1].split('_')[0])


def getRead(fname):
    return int(fname.split('/')[-1].split('R')[1].split('_')[0])


def group_filenames_by_name_read_lane(filenames):
    """Return a dict of dicts where outer keys are (sample_name, read)
    and inner keys are lane numbers. Values are filenames.
    """
    tups = {}
    for fname in filenames:
        key = (getSname(fname), getRead(fname))
        try:
            tups[key]
        except KeyError:
            tups[key] = {}
        tups[key][getLane(fname)] = fname
    return tups


def group_filenames_by_sep(filenames, sep):
    """Return a dict of dicts where outer keys are (sample_name, read)
    and inner keys are lane numbers. Values are filenames.
    """
    tups = {}
    for fname in filenames:
        sample_name = basename(fname).split(sep)[0]
        key = (sample_name, getRead(fname))
        tups[key] = tups.get(key, {})
        tups[key][getLane(fname)] = fname
    return tups


def concatenate_grouped_filenames(grouped, cmd_file=stdout, dryrun=True, dest_dir='.'):
    """Print concat commands to cmd_file. Call the commands if dryrun is False."""
    for (sname, read), val in grouped.items():
        keys = sorted(val.keys())
        filenames = [val[key] for key in keys]
        out = f'{dest_dir}/{sname}_R{read}.fq.gz'
        cmd = f'zcat {" ".join(filenames)} | gzip > {out}'
        print(cmd, file=cmd_file)
        if not dryrun:
            sp.call(cmd, shell=True)
