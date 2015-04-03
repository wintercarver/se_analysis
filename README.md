# se_analysis
## superficial analysis of stack exchange archives.

The User must download the Stack Exchange archives for these scripts to work.

The entire archive is inconveniently large and distributed by bit torrent of 
questionable reliability (as far as seeds goes). Individual sub-archives can
be downloaded and result in directories of the form "<sub-archive-name>.stackexchange.com".

https://archive.org/download/stackexchange

As an example, the archive "academia.stackexchange.com.7z" was downloaded. The 
scripts should be run in this order (after unzipping):
```
$python stack.py academia.stackexchange.com
$python make_plots.py academia.stackexchange.com
```

Final plots will be saved in ./academia.stackexchange.org/plots. By default
the top 5 used tags will have associated time frequency plots and usage per day
of week plots generated. 

The plots take the following name format:
```
freq_<rank>_<tag>_tight.png
days_<rank>_<tag>_tight.png
```
The rank is an integer denoting the rank of the associated tag. The keyword 'tight'
is a superficial plotting tag, indicating margin whitespace is reduced. 

## Brief code description

A small wrapper class was made to facilitate the xml parsing `SEPost()` (stack
exchange post), which strips down the abundance of post information to the necessary
content for these basica plots. 

A second class (`PostArchive()`) to manage the individual posts takes care of the sorting, ranking
and calculation of derived quantities like average scores with minimum view 
requirements.

The basic plotting macros are managed by a class `PlotManager()` and is mostly 
used to organize the kind of ugly matplotlib calls. 


