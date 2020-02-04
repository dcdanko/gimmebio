
from capalyzer.packet_parser import NCBITaxaTree

ROOT_TAXON_NAME = 'root'


class Taxon:
    __tablename__ = 'taxa_tree'

    uuid = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=db.text('uuid_generate_v4()')
    )
    created_at = db.Column(db.DateTime, nullable=False)

    taxa_name = db.Column(db.String(256), index=True, nullable=False)
    taxa_id = db.Column(db.String(256), index=True, nullable=False)
    parent_id = db.Column(UUID(as_uuid=True), index=False, nullable=True)
    rank = db.Column(db.String(256), index=True, nullable=False)

    def __init__(self, taxa_name, taxa_id, parent_id, rank, created_at=datetime.utcnow()):
        self.parent_id = parent_uuid
        self.taxa_name = taxa_name
        self.taxa_id = taxa_id
        self.rank = rank
        self.created_at = created_at

    def parent(self):
        if self.taxa_name == ROOT_TAXON_NAME:
            return None
        return Taxon.query.filter_by(taxa_id=self.parent_id).one()

    @classmethod
    def load_from_tree(cls, ncbi_tree=None):
        """"""
        if ncbi_tree is None:
            ncbi_tree = NCBITaxaTree.parse_files()
        for taxa_id, node in ncbi_tree.nodes_to_name.items():
            taxa_name, rank = node['name'], node['rank']
            parent_id = ncbi_tree.parent_map[taxa_id]
            taxon = cls(taxa_name, taxa_id, parent_id, rank)
            db.session.add(taxon)
        db.session.commit()

    def ancestors(self):
        """Return a list of all ancestors of the taxon starting with the taxon itself."""
        parents = [self]
        parent = self.parent()
        while parent:
            parents.append(parent)
            parent = self.parent()
        return parents

    def ancestor_rank(self, rank, default=None):
        """Return the ancestor of taxon at the given rank."""
        parent = self.parent()
        while parent:
            if rank == parent.rank:
                return parent
            parent = self.parent()
        if not default:
            raise KeyError(f'{rank} for taxa {taxon} not found.')
        return default

    def phyla(self, default=None):
        """Return the phyla for the given taxon."""
        return self.ancestor_rank('phylum', taxon, default=default)

    def genus(self, default=None):
        """Return the genus for the given taxon."""
        return self.ancestor_rank('genus', taxon, default=default)
