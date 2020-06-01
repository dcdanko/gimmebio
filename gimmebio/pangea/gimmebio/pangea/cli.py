
import click
import pandas as pd
from os import environ
from pangea_api import (
    Knex,
    User,
)
from .api import upload_cap_uri_list, link_reads, upload_metadata, upload_reads
from .utils import bcify


@click.group()
def pangea():
    pass


@pangea.group()
def upload():
    pass


@upload.command('cap')
@click.option('--replicate', default=None)
@click.option('--endpoint', default='https://pangea.gimmebio.com')
@click.option('--s3-endpoint', default='https://s3.wasabisys.com')
@click.option('-m', '--module-prefix', default='cap1::')
@click.option('-e', '--email', default=environ.get('PANGEA_USER', None))
@click.option('-p', '--password', default=environ.get('PANGEA_PASS', None))
@click.argument('org_name')
@click.argument('lib_name')
@click.argument('uri_list', type=click.File('r'))
def main(replicate, endpoint, s3_endpoint, module_prefix, email, password, org_name, lib_name, uri_list):
    """Register a list of S3 URIs with Pangea."""
    knex = Knex(endpoint)
    User(knex, email, password).login()
    for field in upload_cap_uri_list(knex, org_name, lib_name,
                                     (line.strip() for line in uri_list),
                                     endpoint_url=s3_endpoint,
                                     threads=1,
                                     module_prefix=module_prefix,
                                     replicate=replicate):
        click.echo(
            f'{field.parent.sample.name} {field.parent.module_name} {field.name}',
            err=True
        )


@pangea.group()
def s3():
    """Functions involving S3."""
    pass


@s3.command('make-uris')
@click.option('-s', '--sep', default='\t')
@click.option('-f', '--filename-list', type=click.File('r'), default='-')
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('prefix')
def make_uri(sep, filename_list, outfile, prefix):
    """Convert a list of filenames to a list suitable for upload to s3.

    filename -> (filename, s3_uri)

    meant for use with xargs as roughly:
        `cat filenames.txt | <this command> | xargs -l <upload_to_s3>`
    """
    assert prefix.startswith('s3://')
    if not prefix.endswith('/'):
        prefix = prefix + '/'
    for line in filename_list:
        path = line.strip()
        fname = path.split('/')[-1]
        print(f'{path}{sep}{prefix}{fname}', file=outfile)


@s3.command('make-cap-uris')
@click.option('-s', '--sep', default='\t')
@click.option('-f', '--filename-list', type=click.File('r'), default='-')
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('bucket_name')
def make_uri(sep, filename_list, outfile, bucket_name):
    """Convert a list of filenames to a list suitable for upload to s3.

    filename -> (filename, s3_uri)

    meant for use with xargs as roughly:
        `cat filenames.txt | <this command> | xargs -l <upload_to_s3>`
    """
    prefix = f's3://{bucket_name}/analysis/metasub_cap1/results/'
    for line in filename_list:
        path = line.strip()
        if path.endswith('.flag.registered'):
            continue
        fname = path.split('/')[-1]
        tkns = fname.split('.')
        if len(tkns) < 4:  # sample name, module name, field name, ext+
            continue
        sample_name = bcify(tkns[0])
        fname = sample_name + '.' + '.'.join(tkns[1:])
        print(f'{path}{sep}{prefix}{sample_name}/{fname}', file=outfile)


@upload.command('link-data')
@click.option('--endpoint', default='https://pangea.gimmebio.com')
@click.option('--s3-endpoint', default='https://s3.wasabisys.com')
@click.option('--index-col', default=0)
@click.option('-m', '--module-name', default='raw::raw_reads')
@click.option('-e', '--email', default=environ.get('PANGEA_USER', None))
@click.option('-p', '--password', default=environ.get('PANGEA_PASS', None))
@click.argument('org_name')
@click.argument('lib_name')
@click.argument('uri_list', type=click.File('r'))
def cli_link_data(endpoint, s3_endpoint, index_col, module_name, email, password, org_name, lib_name, uri_list):
    knex = Knex(endpoint)
    User(knex, email, password).login()
    for sample, ar, r1, r2 in link_reads(knex, org_name, lib_name,
                                         [line.strip().split()[index_col] for line in uri_list],
                                         module_name,
                                         endpoint_url=s3_endpoint,
                                         on_error=lambda e: click.echo(e, err=True)):
        r1uri, r2uri = r1.stored_data['uri'], r2.stored_data['uri']
        click.echo(
            f'{sample.name} {ar.module_name} {r1uri} {r2uri}',
            err=True
        )


@upload.command('reads')
@click.option('--endpoint', default='https://pangea.gimmebio.com')
@click.option('--s3-endpoint', default='https://s3.wasabisys.com')
@click.option('-m', '--module-name', default='raw::raw_reads')
@click.option('-e', '--email', default=environ.get('PANGEA_USER', None))
@click.option('-p', '--password', default=environ.get('PANGEA_PASS', None))
@click.option('-d', '--delim', default=None)
@click.option('-1', '--ext-1', default='.R1.fastq.gz')
@click.option('-2', '--ext-2', default='.R2.fastq.gz')
@click.argument('org_name')
@click.argument('lib_name')
@click.argument('uri_list', type=click.File('r'))
def cli_link_data(endpoint, s3_endpoint, module_name, email, password,
                  delim, ext_1, ext_2,
                  org_name, lib_name, uri_list):
    knex = Knex(endpoint)
    User(knex, email, password).login()
    for sample, ar, r1, r2 in upload_reads(knex, org_name, lib_name,
                                         [line.strip().split()[0] for line in uri_list],
                                         module_name, ext_1, ext_2,
                                         delim=delim,
                                         endpoint_url=s3_endpoint,
                                         on_error=lambda e: click.echo(e, err=True)):
        r1uri, r2uri = r1.stored_data['uri'], r2.stored_data['uri']
        click.echo(
            f'{sample.name} {ar.module_name} {r1uri} {r2uri}',
            err=True
        )


@upload.command('metadata')
@click.option('--create/--no-create', default=False)
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--index-col', default=0)
@click.option('--endpoint', default='https://pangea.gimmebio.com')
@click.option('-e', '--email', default=environ.get('PANGEA_USER', None))
@click.option('-p', '--password', default=environ.get('PANGEA_PASS', None))
@click.argument('org_name')
@click.argument('lib_name')
@click.argument('table', type=click.File('r'))
def cli_metadata(create, overwrite, endpoint, index_col, email, password, org_name, lib_name, table):
    knex = Knex(endpoint)
    User(knex, email, password).login()
    tbl = pd.read_csv(table, index_col=index_col)
    tbl.index = tbl.index.to_series().map(str)
    generator = upload_metadata(
        knex, org_name, lib_name, tbl,
        on_error=lambda e: click.echo(e, err=True), create=create, overwrite=overwrite
    )
    for sample in generator:
        click.echo(sample)


if __name__ == '__main__':
    pangea()
