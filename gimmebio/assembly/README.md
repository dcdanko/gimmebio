# GimmeBio Assembly

Scripts to interpret, run, and analyze metagenomic assemblies.

Interpretation follows these basic steps:
1) Assemble samples using metaSPAdes, assemble from QC'ed reads
2) Find homologous sequences across samples in the same dataset
3) Map contigs to NCBI's NT and keep high quality alignments
4) Find a consensus label for each contig from alignments
5) Condense consensus label to a desired taxonomic rank

### Assembly

Assemble as normal. This procedure was developed for use with metaSPAdes but should be applicable to any metagenomic assembler.

### Finding Homologous Sequences

First we concatenate our scaffolds into a single. We want to be able to track what file each scaffold came from so we use a custom script. This script also has a length filter (default 1kb) for convenience.

```
$ gb assembly cat-fastas concat_scaffolds.fasta *.mspades/scaffolds.fasta
```

Next we make a blast database using our concatenated scaffolds and align them against themselves. The `filter-homologous` script has parameters for minimum alignment length and minimum percent identity (default 1kbp, 95%). The script will pick the longest assembly as the representative.

```
$ makeblastdb 
    -dbtype nucl 
    -in concat_scaffolds.fasta 
    -out concat_scaffolds.blastdb
$ blastn 
    -db concat_scaffolds.blastdb 
    -outfmt 6 
    -perc_identity 80 
    -query concat_scaffolds.fasta 
    > concat_scaffolds.self_align.m8
$ gb assembly filter-homologous deduped.concat_scaffolds.fasta concat_scaffolds.self_align.m8 concat_scaffolds.fasta 
```

The deduplicated scaffolds can now be found in `deduped.concat_scaffolds.fasta`


### Map to NT and Classify Scaffolds

Mapping to NCBI-NT is straightforward.

```
$ blastn 
    -db <path/to/ncbi/nt> 
    -outfmt 6 -perc_identity 80 
    -query deduped.concat_scaffolds.fasta 
    > deduped.concat_scaffolds.ncbi_nt.m8
```

Classification based on alignments is a little trickier. At a minimum we want to group alignments from the same scaffold to the same taxon into a single record. Depending on the situation we may also want to pick a single classification for each scaffold.

We will need a file that maps NCBI taxa-IDs to useful taxa names. We refer to this as `taxa_map.csv.gz`

To group alignments without picking a single winner we run the following. 

```
$ gb assembly id-contigs 
    -g taxa_map.tsv.gz 
    -f deduped.concat_scaffolds.fasta
    deduped.concat_scaffolds.ncbi_nt.m8
    deduped.concat_scaffolds.taxa_ids.csv
```

Currently we only support one strategy to pick a single taxonomic id for each scaffold, _winner takes all_. After finding a set of taxonomic ids for each scaffold we check which taxonomic ids have the most support across all scaffolds and choose those as the winners. All scaffolds are assigned to exactly one winner. This is essentially an assumption of homology.

To run _winner takes all_ just add a flag to the above command `--winner-takes-all`

### Condense to a Desired Rank

Optionally we might want to reduce or classifications to a higher taxonomic rank (We get strain level assignments from NCBI-NT typically) like genus or species. If we think our assembly includes a novel species or strain this can help simplify analysis.

```
$ gb assembly condense-ids 
    -r genus 
    deduped.concat_scaffolds.taxa_ids.csv  
    deduped.concat_scaffolds.genus_ids.csv
```

