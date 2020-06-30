
import hashlib
import boto3
import os

from sqlalchemy import create_engine
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class MissingChecksumException(Exception):
    pass


class ChecksumMismatchException(Exception):
    pass


class LocalFile(Base):

    __tablename__ = 'local_file'
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)
    md5sum = Column(String)

    def add_checksum(self):
        if self.md5sum:
            return
        md5 = hashlib.md5(open(self.path, 'rb').read()).hexdigest()
        self.md5sum = md5

    def __str__(self):
        return (
            f'<LocalFile '
            f'id={self.id} '
            f'path={self.path} '
            f'md5sum={self.md5sum} '
            f'/>'
        )

class S3ApiKey(Base):

    __tablename__ = 's3_api_key'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    endpoint_url = Column(String)
    access_key = Column(String)
    access_secret = Column(String)

    def __str__(self):
        return (
            f'<S3ApiKey '
            f'id={self.id} '
            f'name={self.name} '
            f'endpoint_url={self.endpoint_url} '
            f'access_key={self.access_key} '
            f'access_secret={self.access_secret[:6]}... '
            f'/>'
        )


class S3File(Base):

    __tablename__ = 's3_file'
    __table_args__ = (
        UniqueConstraint('key_id', 'uri', name='_key_uri_uc'),
    )
    id = Column(Integer, primary_key=True)
    key_id = Column(Integer, ForeignKey('s3_api_key.id'))
    key = relationship("S3ApiKey")
    local_file_id = Column(Integer, ForeignKey('local_file.id'))
    local_file = relationship("LocalFile")
    uri = Column(String)
    md5sum = Column(String)
    uploaded = Column(Boolean, default=False)

    @property
    def s3(self):
        if getattr(self, '_s3', None):
            return self._s3
        self._s3 = boto3.client(
            's3',
            aws_access_key_id=self.key.access_key,
            aws_secret_access_key=self.key.access_secret,
            endpoint_url=self.key.endpoint_url,
        )
        return self.s3

    @property
    def bucket_name(self):
        return self.uri.split('s3://')[1].split('/')[0]

    @property
    def s3_file_path(self):
        return self.uri.split(self.bucket_name + '/')[1].replace('//', '/')

    def upload(self):
        """Upload the attached local file to S3."""
        if self.uploaded:
            return
        self.s3.upload_file(self.local_file.path, self.bucket_name, self.s3_file_path)
        self.uploaded = True

    def download(self, download_dir):
        save_as = f'{download_dir}/{self.s3_file_path}'
        os.makedirs(os.path.dirname(save_as), exist_ok=True)
        self.s3.download_file(self.bucket_name, self.s3_file_path, save_as)
        return save_as

    def download_then_add_checksum(self, download_dir, remove=True):
        if self.md5sum:
            return
        path = self.download(download_dir)
        md5 = hashlib.md5(open(path, 'rb').read()).hexdigest()
        self.md5sum = md5
        if remove:
            os.remove(path)
        return self.md5sum

    def validate(self):
        """Raise an exception if the checksum does not exist or if it does not match the local file.

        Return true otherwise
        """
        if not self.md5sum:
            raise MissingChecksumException(f'{self} has no checksum')
        if not self.local_file.md5sum:
            raise MissingChecksumException(f'{self.local_file} has no checksum')
        if self.md5sum != self.local_file.md5sum:
            raise ChecksumMismatchException(f'Checksum for {self} does not match {self.local_file}')
        return True

    def __str__(self):
        return (
            f'<S3File '
            f'id={self.id} '
            f'key={self.key.name} '
            f'local_file_id={self.local_file_id} '
            f'uri={self.uri} '
            f'md5sum={self.md5sum} '
            f'uploaded={self.uploaded} '
            f'/>'
        )
