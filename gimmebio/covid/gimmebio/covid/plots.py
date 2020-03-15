
import pandas as pd
from plotnine import *


def to_title(el):
    sel = str(el)
    if not el:
        return el
    tkns = sel.split('_')
    tkns = [tkn[0].upper() + tkn[1:] for tkn in tkns]
    return ' '.join(tkns)


def taxa_plot(tbl):
    toplot = []
    for pid in [99, 95, 90, 80]:
        for k, v in tbl.query(f'pident >= {pid}')['sseqid'].value_counts().iteritems():
            species, strain, contig = k.split('___')
            toplot.append({
                'species': species,
                'strain': strain,
                'species_strain': to_title(f'{species}, {strain}'),
                'contig': contig,
                'percent_identity': str(pid),
                'num_reads': v,
            })
    toplot = pd.DataFrame.from_dict(toplot)
    return (
        ggplot(toplot, aes(x='species_strain', y='num_reads', fill='percent_identity')) +
            geom_col(position='dodge') +
            theme_minimal() +
            ylab('Num. Reads') +
            scale_y_log10() +
            scale_fill_brewer(type='qualitative', palette=6, direction=1) +
            labs(fill="Percent Identity") +
            coord_flip() +
            theme(
                axis_title_y=element_blank(),
                text=element_text(size=20),
                #panel_grid_major=element_blank(),
                legend_position='right',
                figure_size=(8, 8),
                panel_border=element_rect(colour="black", fill='none', size=1),
            )
    )


def coverage_plot(tbl):
    #tbl = tbl.query(f'pident >= 90')
    
    def cat_pid(x):
        if x >= 99:
            return '99'
        if x >= 95:
            return '95'
        if x >= 90:
            return '90'
        if x >= 80:
            return '80'
    
    tbl['percent_identity'] = tbl['pident'].map(cat_pid)
    tbl['species_strain'] = tbl['sseqid'].map(lambda x: to_title(', '.join(x.split('___')[:2])))
    tbl['condensed_start'] = tbl['sstart'].map(lambda x: x // 100)
    return (
        ggplot(tbl, aes(x='condensed_start', fill='percent_identity')) +
            geom_bar(position='dodge') +
            facet_wrap('~species_strain', scales="free_y", ncol=1) +
            theme_minimal() +
            ylab('Num. Reads') +
            xlab('Start Position (100bp Increments)') +
            scale_fill_brewer(type='qualitative', palette=6) +
            scale_y_log10() +
            labs(fill='Percent Id.') +
            theme(
                text=element_text(size=20),
                legend_position='right',
                figure_size=(12, 4 * tbl['species_strain'].nunique()),
                panel_border=element_rect(colour="black", fill='none', size=1),
            )
    )
