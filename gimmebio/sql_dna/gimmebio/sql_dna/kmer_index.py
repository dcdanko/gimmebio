
from sqlalchemy.dialects.postgresql import UUID

from .db import db
from gimmebio.kmers import make_kmers
from .contig import Contig

MAX_K = 31


class KmerContainment(db.Model):
    __tablename__ = 'organization_memberships'

    kmer = db.Column(db.String(31), index=True, nullable=False)
    seq_uuid = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('contigs.uuid'),
        index=False,
        nullable=False
    )

    def __init__(self, seq_uuid, kmer):
        self.kmer = kmer
        self.seq_uuid = seq_uuid

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def add_contig(cls, contig):
        kmers = set(make_kmers(contig.seq, MAX_K))
        for kmer in kmers:
            db.session.add(cls(contig.uuid, kmer))
        db.session.commit()

    @classmethod
    def kmer_search(cls, seq, eps=0.5):
        uuids = {}
        kmers = make_kmers(seq, MAX_K)
        for kmer in kmers:
            for uuid in cls.query.filter_by(kmer=kmer).all():
                uuids[uuid] = uuids.get(uuid, 0) + 1
        seqs = []
        for uuid, count in uuids.items():
            if count < (eps * len(kmers)):
                continue
            seqs.append(Contig.from_uuid(uuid))
        return seqs
