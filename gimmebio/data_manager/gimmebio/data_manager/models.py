
import hashlib

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
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
        md5 = hashlib.md5(open(self.path,'rb').read()).hexdigest()
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
    local_file_id = Column(Integer, ForeignKey('local_file.id'))
    uri = Column(String)
    md5sum = Column(String)

    def upload(self):
        """Upload the attached local file to S3."""
        pass

    def download_then_add_checksum(self):
        pass

    def validate(self):
        """Raise an exception if the checksum does not exist or if it does not match the local file.

        Return true otherwise
        """
        pass
