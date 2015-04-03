# se_analysis
superficial analysis of stack exchange archives.

The User must download the Stack Exchange archives for these scripts to work.

The entire archive is inconveniently large and distributed by bit torrent of 
questionable reliability (as far as seeds goes). Individual sub-archives can
be downloaded and result in directories of the form "<sub-archive-name>.stackexchange.com".

https://archive.org/download/stackexchange

As an example, the archive "academia.stackexchange.com.7z" was downloaded. The 
scripts should be run in this order (after unzipping):

$python stack.py academia.stackexchange.com
$python make\_plots.py academia.stackexchange.com

Final plots will be saved in ./academia.stackexchange.org/plots. By default
the top 5 used tags will have associated time frequency plots and usage per day
of week plots generated. 


