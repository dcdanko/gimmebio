
import click

from os.path import abspath

from .models import (
    LocalFile,
    S3ApiKey,
    S3File,
    MissingChecksumException,
    ChecksumMismatchException,
)
from .db import get_session


@click.group()
def data():
    pass


@data.command('validate')
@click.option('-d', '--database', type=click.Path(), default=None)
@click.option('-p/-f', '--passed/--failed', default=True, help='Show files where validation failed')
@click.option('-x/-n', '--xml/--filenames', default=True, help='Print local filenames')
def cli_validate(database, passed, xml):
    session = get_session(database)
    for s3_file in session.query(S3File).all():
        try:
            s3_file.validate()
        except MissingChecksumException:
            continue
        except ChecksumMismatchException:
            if not passed:
                if xml:
                    click.echo(s3_file)
                else:
                    click.echo(s3_file.local_file.path)
            continue
        if passed:
            if xml:
                click.echo(s3_file)
            else:
                click.echo(s3_file.local_file.path)


@data.group('add')
def cli_add():
    pass


@cli_add.command('key')
@click.option('-d', '--database', type=click.Path(), default=None)
@click.option('-e', '--endpoint-url', default='https://s3.wasabisys.com')
@click.argument('name')
@click.argument('access_key')
@click.argument('access_secret')
def cli_add_key(database, endpoint_url, name, access_key, access_secret):
    """Add local files to the database."""
    session = get_session(database)
    paths = set(session.query(LocalFile).all())
    key = S3ApiKey(name=name, endpoint_url=endpoint_url, access_key=access_key, access_secret=access_secret)
    session.add(key)
    session.commit()
    click.echo(f'Added key {name}: {key}', err=True)


@cli_add.command('files')
@click.option('-d', '--database', type=click.Path(), default=None)
@click.option('-l', '--filepath-list', type=click.File('r'), default='-')
def cli_add_files(database, filepath_list):
    """Add local files to the database."""
    session = get_session(database)
    paths = {f.path for f in session.query(LocalFile).all()}
    n_new_files = 0
    for i, filepath in enumerate(filepath_list):
        path = abspath(filepath.strip())
        if path in paths:
            continue
        local_file = LocalFile(path=path)
        n_new_files += 1
        session.add(local_file)
        if i > 0 and i % 1000 == 0:
            session.commit()
    session.commit()
    click.echo(f'Added {n_new_files} new files.', err=True)


@cli_add.command('s3-remote')
@click.option('-d', '--database', type=click.Path(), default=None)
@click.option('-k', '--key-name')
@click.argument('s3_prefix')
def cli_add_s3_remote(database, key_name, s3_prefix):
    """Add a corresponding S3 file to every file in the database."""
    s3_prefix = s3_prefix[:-1] if s3_prefix.endswith('/') else s3_prefix
    s3_prefix = s3_prefix if s3_prefix.startswith('s3://') else 's3://' + s3_prefix
    session = get_session(database)
    key = session.query(S3ApiKey).filter(S3ApiKey.name == key_name).first()
    remote_uris = {f.uri for f in session.query(S3File).all()}
    n_new_remotes = 0
    for i, local in enumerate(session.query(LocalFile).all()):
        uri = f'{s3_prefix}/{local.path}'
        if uri in remote_uris:
            continue
        remote_file = S3File(key=key, local_file=local, uri=uri)
        session.add(remote_file)
        n_new_remotes += 1
        if i > 0 and i % 1000 == 0:
            session.commit()
    session.commit()
    click.echo(f'Added {n_new_remotes} new remote files.', err=True)


@data.group('run')
def cli_list():
    pass


@cli_list.command('md5')
@click.option('-d', '--database', type=click.Path(), default=None)
def cli_run_md5(database):
    """Compute md5 sums for local files."""
    session = get_session(database)
    for i, local_file in enumerate(session.query(LocalFile).all()):
        click.echo(f'Checksuming {local_file}')
        try:
            local_file.add_checksum()
            session.commit()
        except Exception:
            click.echo(f'Checksum failed for {local_file}')
    session.commit()


@cli_list.command('upload')
@click.option('-d', '--database', type=click.Path(), default=None)
def cli_run_md5(database):
    """Upload remote files."""
    session = get_session(database)
    for i, s3_file in enumerate(session.query(S3File).all()):
        click.echo(f'Uploading {s3_file} to bucket: {s3_file.bucket_name} path: {s3_file.s3_file_path}')
        try:
            s3_file.upload()
            session.commit()
        except Exception:
            click.echo(f'Upload failed for {s3_file}')
    session.commit()


@cli_list.command('remote-md5')
@click.option('-d', '--database', type=click.Path(), default=None)
@click.argument('download_dir')
def cli_run_md5(database, download_dir):
    """Compute md5 sums for remote files."""
    session = get_session(database)
    for i, s3_file in enumerate(session.query(S3File).all()):
        click.echo(f'Downloading {s3_file}')
        try:
            s3_file.download_then_add_checksum(download_dir)
            session.commit()
        except Exception:
            click.echo(f'Download or checksum failed for {s3_file}')
    session.commit()


@data.group('list')
def cli_list():
    pass


@cli_list.command('keys')
@click.option('-d', '--database', type=click.Path(), default=None)
def cli_list_keys(database):
    session = get_session(database)
    for key in session.query(S3ApiKey).all():
        click.echo(key)


@cli_list.command('files')
@click.option('-d', '--database', type=click.Path(), default=None)
def cli_list_file(database):
    session = get_session(database)
    for local_file in session.query(LocalFile).all():
        click.echo(local_file)


@cli_list.command('s3-remotes')
@click.option('-d', '--database', type=click.Path(), default=None)
def cli_list_s3_remtoes(database):
    session = get_session(database)
    for s3_file in session.query(S3File).all():
        click.echo(s3_file)
