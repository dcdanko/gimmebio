import gzip
import sys
import subprocess as sp
import numpy as np
import pandas as pd

phylumtokingdom="""
Poribacteria
Bacteria

Verrucomicrobia
Bacteria

Bacteroidetes
Bacteria

Thermotogae_<phylum>
Bacteria

Elusimicrobia   
Bacteria

Chloroflexi_<phylum>    
Bacteria

Chlorobi        
Bacteria

Tenericutes     
Bacteria

Lentisphaerae   
Bacteria

Chrysiogenetes_<phylum> 
Bacteria

Thermodesulfobacteria_<phylum> 
Bacteria

Dictyoglomi     
Bacteria

Nitrospirae     
Bacteria

Deinococcus-Thermus     
Bacteria

Ignavibacteria_<phylum> 
Bacteria

Proteobacteria  
Bacteria

Acidobacteria   
Bacteria

Spirochaetes    
Bacteria

Firmicutes      
Bacteria

Thaumarchaeota  
Archaea

Planctomycetes  
Bacteria

Fusobacteria    
Bacteria

Synergistetes   
Bacteria

Actinobacteria_<phylum> 
Bacteria

Crenarchaeota   
Archaea

Aquificae_<phylum>     
Bacteria

Korarchaeota    
Archaea

Gemmatimonadetes
Bacteria

Chlamydiae      
Bacteria

Armatimonadetes 
Bacteria

Cyanobacteria   
Bacteria

Caldiserica     
Bacteria

Deferribacteres_<phylum>      
Bacteria

Fibrobacteres   
Bacteria

Euryarchaeota   
Archaea

Nanoarchaeota
Archaea
"""


def countAligned(alignfile,p2k):
    species = alignfile.split('/')[-1].split('.')[0].split('-')[0].split('_')[0]
    if 'sheep' in alignfile:
        species = 'sheep'
    if 'cow' in alignfile:
        species='cow'
    sind = alignfile.index('phylum')
    sfile = alignfile[:sind] + 'species' + alignfile[sind+6:]
#    print(sfile)
    
    out = {
        'Bacteria':0,  
        'Viruses':0,
        'Eukaryota':0, 
        'Archaea':0,           
    }
    with gzip.open(alignfile) as af:
        for line in af:
            line = line.split()
            if len(line) != 2 or 'taxa' in line[0]:
                continue
            k = p2k[line[0].strip()]
#            print("{} -> {} ({})".format(line[0].strip(),k,int(line[1])))
            out[k] = out[k] + int(line[1])
    try:
        cmd = "zcat {} | grep -i 'virus'".format(sfile)
        data = sp.check_output(cmd,shell=True)
        for line in data.split('\n'):
            line = line.split()
            if len(line) != 2 or 'Sample' in line[0]:
                continue
            k = 'Viruses'
            out[k] = out[k] + int(line[1])
    except:
        pass
    
    out['Bacteria'] = out['Bacteria'] - out['Viruses']
    N = sum([v for v in out.values()])
    for k,v in out.items():
        out[k] = 1000*1000*float(v)/N
    return (species, out)


def mergeAligned(outputs):
    merged = {}
    for species, out in outputs:
        for kind, val in out.items():
            if kind not in merged:
                merged[kind] = {}
            if species not in merged[kind]:
                merged[kind][species] = []
            merged[kind][species].append(val)
    return merged

def buffer(outputs):
    buff = {}
    for species, out in outputs:
        if species not in buff:
            buff[species] = []
        buff[species].append(out)

    for species,outs in buff.items():
        top = 0
        if len(outs) > len(top):
            top = len(outs)
        for out in outs:
            for _ in range(top - len(out)):
                out.append(0)
    

def crunchAligned(merged):
    crunched = {kind:{} for kind in merged.keys()}
    for kind, val in merged.items():
        for species, vals in val.items():
            u = np.mean(vals)
            sd = np.std(vals)
            crunched[kind][species] = (u,sd)
    return crunched

def prettyprint(crunched):
    print("\n--------------------------------------------------------\n")
    outline = "{:.1f} ({:.1f}) \t& {:.1f} ({:.1f}) \t& {:.1f} ({:.1f}) \t& {:.1f} ({:.1f}) \t\\\\"
    for row in crunched.itertuples():
        print(row)
        ar = []
        for v in row[1:]:
  #          print(v)
            ar.append(float(v[0]))
            ar.append(float(v[1]))
 #       print(ar)
        print(outline.format(*ar))
        
    
def main(args):
    if len(args) == 0:
        print("Usage: metaphlan-profile-files")
        return 1

    p2k = {}
    a = phylumtokingdom.split('\n')
    a = [v for v in a if len(v) > 0]
    for i in range(0,len(a),2):
        p2k[a[i].strip()] = a[i+1].strip()

    for k,v in p2k.items():
        print("{} : {}".format(k,v))
    
    outputs = []
    for f in args:
        a = countAligned(f,p2k)
        if not a:
            continue
        outputs.append(a)
    
    merged = mergeAligned(outputs)
    crunched = crunchAligned(merged)
    crunched = pd.DataFrame(crunched)
    print(crunched)
    prettyprint(crunched)
    
if __name__ == '__main__':
    main(sys.argv[1:])
