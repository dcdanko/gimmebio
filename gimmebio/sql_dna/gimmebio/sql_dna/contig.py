
import json
from datetime import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from .db import db


MAX_SEQ_LEN = 10 * 1000


class Contig(db.Model):
    """Represent a contig in the database."""

    __tablename__ = 'contigs'

    uuid = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=db.text('uuid_generate_v4()')
    )
    created_at = db.Column(db.DateTime, nullable=False)

    genome_name = db.Column(db.String(256), index=True, nullable=False)
    contig_name = db.Column(db.String(256), index=False, nullable=False)
    start_pos = db.Column(db.Integer)
    length = db.Column(db.Integer)
    seq = db.Column(db.String(MAX_SEQ_LEN), index=False, nullable=False)

    def __init__(  # pylint: disable=too-many-arguments
            self, genome_name, contig_name, start_pos, seq
            created_at=datetime.utcnow()):
        self.genome_name = genome_name
        self.contig_name = contig_name
        self.start_pos = start_pos
        self.length = len(seq)
        self.seq = seq
        self.created_at = created_at

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def from_uuid(cls, uuid):
        return cls.query.filter_by(uuid=uuid).one()

    @classmethod
    def ingest_fasta(cls, genome_name, fasta_file, block_size=MAX_SEQ_LEN):
        for rec in SeqIO.parse(fasta_file, 'fasta'):
            for start in range(0, len(rec.seq), block_size):
                end = min(len(block_size), start + block_size)
                seq = rec.seq[start, end]
                contig = cls(genome_name, rec.id, start_pos, seq)
                db.session.add(contig)
        db.session.commit()
