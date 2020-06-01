
import json

from multiprocessing import Pool, Lock
from pangea_api import (
    Organization,
    RemoteObjectOverwriteError,
)
from .utils import (
    bcify,
    caching_get_sample,
    caching_get_sample_ar,
)
from .constants import WASABI_URL


def upload_one_cap_uri(lib, uri, endpoint_url=WASABI_URL, module_prefix='', lock=None, replicate=None):
    fname = uri.split('/')[-1]
    sample_name, module_name, field_name = fname.split('.')[:3]
    module_name = module_prefix + module_name
    sample_name = bcify(sample_name)
    if lock:
        lock.acquire()
    sample = caching_get_sample(lib, sample_name)
    ar = caching_get_sample_ar(sample, module_name, replicate=replicate)
    if lock:
        lock.release()
    field = ar.field(field_name, {
        '__type__': 's3',
        'endpoint_url': endpoint_url,
        'uri': uri,
    }).idem()
    return field


def upload_one_cap_uri_wrapper(args):
    try:
        return upload_one_cap_uri(
            args[0], args[1], endpoint_url=args[2], module_prefix=args[3], lock=args[4],
            replicate=args[5]
        )
    except RemoteObjectOverwriteError:
        pass


def upload_cap_uri_list(knex, org_name, lib_name, uri_list, 
                        threads=1, endpoint_url=WASABI_URL, module_prefix='', on_error=None,
                        replicate=None):
    org = Organization(knex, org_name).get()
    lib = org.sample_group(lib_name).get()
    lock = Lock()
    upload_args = [(lib, uri, endpoint_url, module_prefix, lock, replicate) for uri in uri_list]
    if threads == 1:
        for args in upload_args:
            try:
                field = upload_one_cap_uri_wrapper(args)
                if field:
                    yield field
            except ValueError:
                pass
            except Exception as e:
                if on_error:
                    on_error(e)
                else:
                    raise
    else:  # currently broken
        with Pool(threads) as pool:
            for field in pool.imap_unordered(upload_one_cap_uri_wrapper, upload_args):
                yield field


def upload_metadata(knex, org_name, lib_name, tbl, on_error=None, create=False, overwrite=False):
    org = Organization(knex, org_name).get()
    lib = org.sample_group(lib_name).get()
    for sample_name, row in tbl.iterrows():
        sample = lib.sample(sample_name)
        if create:
            sample = sample.idem()
        else:
            try:
                sample = sample.get()
            except Exception as e:
                if on_error:
                    on_error(e)
                    continue
                else:
                    raise
        if overwrite or (not sample.metadata):
            sample.metadata = json.loads(json.dumps(row.dropna().to_dict()))
            sample.idem()
        yield sample


def link_reads(knex, org_name, lib_name, uri_list, module_name, endpoint_url=WASABI_URL, on_error=None):
    org = Organization(knex, org_name).get()
    lib = org.sample_group(lib_name).get()

    def uri_contains_name(name, uri):
        if name not in uri:
            if 'BC-0' in name:
                return uri_contains_name(name.split('BC-0')[1], uri)
            return False
        tkns = uri.split(name)
        try:
            if tkns[1][0] in '_-.':
                return True
            return False
        except KeyError:
            return False

    for sample in lib.get_samples():
        reads = [uri for uri in uri_list if uri_contains_name(sample.name, uri)]
        reads = sorted(reads)
        if len(reads) != 2:
            if on_error:
                on_error(ValueError(f'Sample {sample.name} has wrong number of reads: {reads}'))
            continue
        ar = sample.analysis_result(module_name)
        r1 = ar.field('read_1', data={
            '__type__': 's3',
            'endpoint_url': endpoint_url,
            'uri': reads[0],
        }).idem()
        r2 = ar.field('read_2', data={
            '__type__': 's3',
            'endpoint_url': endpoint_url,
            'uri': reads[1],
        }).idem()
        yield sample, ar, r1, r2


def upload_reads(knex, org_name, lib_name, uri_list, module_name,
                 r1_ext, r2_ext, delim=None, endpoint_url=WASABI_URL,
                 on_error=None):
    org = Organization(knex, org_name).get()
    lib = org.sample_group(lib_name).get()

    samples = {}
    for uri in uri_list:
        if r1_ext in uri:
            sname = uri.split(r1_ext)[0]
            key = 'read_1'
        if r2_ext in uri:
            sname = uri.split(r2_ext)[0]
            key = 'read_2'
        sname = sname.split('/')[-1]
        if delim:
            sname = sname.split(delim)[0]
        if sname not in samples:
            samples[sname] = {}
        samples[sname][key] = uri

    for sname, reads in samples.items():
        if len(reads) != 2:
            if on_error:
                on_error(ValueError(f'Sample {sname} has wrong number of reads: {reads}'))
            continue
        sample = lib.sample(sname).idem()
        ar = sample.analysis_result(module_name)
        r1 = ar.field('read_1', data={
            '__type__': 's3',
            'endpoint_url': endpoint_url,
            'uri': reads['read_1'],
        }).idem()
        r2 = ar.field('read_2', data={
            '__type__': 's3',
            'endpoint_url': endpoint_url,
            'uri': reads['read_2'],
        }).idem()
        yield sample, ar, r1, r2
