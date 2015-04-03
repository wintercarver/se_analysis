#!/usr/bin/python
import sys
from stackexchange import PostArchive
from xml.etree import ElementTree
import datetime
import matplotlib.dates as mdates
import os

def prepare_output_directories(archive_name):
  """Take an input archive name, ensure it exists and create a 'results' and
  'plots' directory to house related analysis output content."""

  if os.path.exists(archive_name):
    results_dir = os.path.join(archive_name,'results')
    plots_dir = os.path.join(archive_name,'plots')
    if not os.path.exists(results_dir):
      print 'Making results directory:\n\t{0}'.format(results_dir)
      os.makedirs(results_dir)
    if not os.path.exists(plots_dir):
      print 'Making plots directory:\n\t{0}'.format(plots_dir)
      os.makedirs(plots_dir)
  else:
    print 'Archive to analyze not found, check for {0}.'.format(archive_name)
    quit()

def main(argv):

  archive_name = argv[1]
  prepare_output_directories(archive_name)
  
  # Feed xml archive into parser.
  try:
    posts_file = os.path.join(archive_name,'Posts.xml')
    with open(posts_file, mode='r') as f:
      tree = ElementTree.parse(f)
  except:
      print '{0} not found. Exiting.'.format(
          os.path.join(archive_name,'Posts.xml'))
    
  # Create database from xml archive. Initialization will parse the xml file.
  db = PostArchive(tree, archive_name)

  SORT_COUNT, SORT_SCORE, SORT_AVG = range(3)
  SORT_VIEWS = 1
  print '----'
  db.PrintTopTags(SORT_COUNT)
  print '----'
  db.PrintTopTags(SORT_VIEWS)
  print '----'
  db.PrintTopTags(SORT_AVG)
  print '----'
  db.PrintTopUsers(SORT_COUNT)
  print '----'
  db.PrintTopUsers(SORT_SCORE)
  print '----'
  db.PrintTopUsers(SORT_AVG)
  print '----'
  db.PrintDateRange()

  db.SaveTagDateData()
  print '----\n\n'

if __name__ == "__main__":
  if(len(sys.argv) != 2):
    print 'Run script with reference to archive directory:\n\t \
            ./python stack.py <archive>'
    quit()
  main(sys.argv)
