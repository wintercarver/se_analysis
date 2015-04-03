#!/usr/bin/python
from xml.etree import ElementTree
import datetime
import matplotlib.dates as mdates
import os

class SEPost(object):
  def __init__(self,a_node):
    """
    Process a single row of the stack exchange data.
    Take a row (aka "node") as input, extract:
      -tag info
      -date of post (format:)
      -post owner unique ID (no name available)
      -post view count
      -post score count
      -stack exchange sub-rchive name (e.g. "academia","mathematics",etc)

    The above variables are the raw data necessary for analysis.
    derived variables are:
      -total cumulative post score per user
      -total cumulative post count per user
      -average score per post per user
      -cumulative use count per tag
      -number of views per tag
    """

    # Tag data comes in the string form '<tag1><tag2>...<tagN>'
    # or is equal to 'None' for no tags. Slice on tag string and then
    # splitting '><' creates a human-readable list of tags.
    self.tags = str(a_node.attrib.get('Tags'))
    if self.tags == 'None':
      self.tags=[]
    else:
      self.tags = self.tags[1:-1].split('><')

    # Owner display name is only used for users that have been removed and do 
    # not have a user ID. Display names are strings of form "userXXX" where
    # XXX is a three-digit interger (as far as I can tell).
    self.OwnerDisplayName = a_node.attrib.get('OwnerDisplayName')
    if self.OwnerDisplayName == None:
      self.OwnerDisplayName = -1
    else:
      self.OwnerDisplayName = a_node.attrib.get('OwnerDisplayName')

    # There should alway be a positive user ID. 
    self.UserId = str(a_node.attrib.get('OwnerUserId'))
    if self.UserId == 'None':
      self.UserId = -1
    else:
      self.UserId = int(a_node.attrib.get('OwnerUserId'))

    # Get view count for the post.
    self.ViewCount = str(a_node.attrib.get('ViewCount'))
    if self.ViewCount == 'None':
      self.ViewCount = -1
    else:
      self.ViewCount = int(a_node.attrib.get('ViewCount'))

    # Get score for the post.
    self.PostScore = str(a_node.attrib.get('Score'))
    if self.PostScore == 'None':
      self.PostScore = None
    else:
      self.PostScore = int(a_node.attrib.get('Score'))

    # Get score for the post type ID.
    # 1 == Question
    # 2 == Answer
    self.PostTypeId = str(a_node.attrib.get('PostTypeId'))
    if self.PostTypeId == 'None':
      self.PostTypeId = None
    else:
      self.PostTypeId = int(a_node.attrib.get('PostTypeId'))


    # Process creation date string, store as datetime object.
    date_string = str(a_node.attrib.get('CreationDate'))
    if date_string != 'None':
      self.CreationDate = datetime.datetime.strptime(
          date_string, "%Y-%m-%dT%H:%M:%S.%f")
    else:
      self.CreationDate = datetime.datetime.strptime("1900-01-01", "%Y-%m-%d")
  # End __init()__

  def GetTags(self):
    """Return list of tags used in post, or an empty list for no tags."""
    return self.tags

  def GetUserId(self):
    """Return unique user ID (int)."""
    return self.UserId

  def GetOwnerDisplayName(self):
    """Return  user display name (-1 if null)."""
    return self.OwnerDisplayName

  def GetViewCount(self):
    """Return view count (int) for post."""
    return self.ViewCount

  def GetPostScore(self):
    """return view count (int) for post."""
    return self.PostScore

  def GetPostType(self,as_string=False):
    """Return the post type ID, as int or as string.
    1 == question, 2 == answer"""
    if as_string == False:
      return self.PostTypeId
    else:
      return 'question' if self.PostTypeId == 1 else 'answer'

  def GetArchiveName(self):
    """Return name of stack exchange archive as string
    e.g. "mathematics", "academia", etc."""
    #not implemented, may use in future
    pass

  def GetCreationDate(self):
    """Return post creation date as datetime object."""
    return self.CreationDate

##############
class PostArchive():
  def __init__(self, xml_tree, archive_name):
    """
    Initialization accepts an xml archive from the stack exchange data. 
    All posts are sorted and pertinent information for the view counts, scores
    and tag information is processed. An associated archive name is stored and
    results are stored to a results directory in the archive directory.

    """
    self.archive = archive_name
    self.all_posts = list()
    self.user_summary = dict()
    self.tag_summary = dict()

    # Parse xml archive and create a list of stack exchange post objects.
    invalid_users = 0
    display_users = 0
    for node in xml_tree.iter():
      a_post = SEPost(node)
      if a_post.GetUserId() == -1:
        invalid_users += 1
        if a_post.GetOwnerDisplayName() != None:
          display_users += 1
        continue 
      self.all_posts.append(a_post)
    print '{0} invalid (no creation owner ID) posts found.\n'.format(invalid_users)
    print '{0} display (no creation owner ID) posts found.\n'.format(display_users)
    print 'Invalid posts should equal the number of display posts.\n'

    # Set default earliest and latest post dates to a date in the middle
    # of the archive. Will sort for first and last post dates when iterating
    # over all of the posts. Null date is a dummy value for bad entries.
    mid_date = datetime.datetime.strptime("2014-01-01", "%Y-%m-%d")
    null_date = datetime.datetime.strptime("1900-01-01", "%Y-%m-%d")
    self.first_post_date = mid_date
    self.last_post_date = mid_date

    # Iterate over all posts and extract cumulative metrics specifics to 
    # users and tags. After iteration over posts, derived values (e.g. averages)
    # are calculated. Also, store the first and last post date.
    for post in self.all_posts:

      # Calculate the cumulative posts and score PER USER.
      user_id = post.GetUserId()
      score = post.GetPostScore()
      try:
        self.user_summary[user_id][0] += 1
        self.user_summary[user_id][1] += score
      except:
        self.user_summary[user_id] = [1,score,0] 

      # Calculate the cumulative uses and views PER TAG.
      tag_list = post.GetTags()
      viewcount = post.GetViewCount()
      for tag in tag_list:
        try:
          self.tag_summary[tag][0] += 1
          self.tag_summary[tag][1] += viewcount
        except:
          self.tag_summary[tag] = [1, viewcount, 0]

      # Search for post date boundaries
      post_date = post.GetCreationDate()
      if post_date < self.first_post_date and post_date != null_date:
        self.first_post_date = post_date
      if post_date > self.last_post_date and post_date != null_date:
        self.last_post_date = post_date
    # End of iteration over all posts #
     
    # Calculate average score per post for each user:
    # val is a list of form [number_of_posts, cumulative_score, avergage_score]
    # where the average_score variable is calculated in this dict comprehension.
    self.user_summary = {
      user_id:[val[0],val[1],round(float(val[1])/val[0],1)] for 
      user_id,val in self.user_summary.items()}

    # Calculate the average view per use for each tag:
    # val is a list of form [number_of_uses, cumulative_views, avergage_view]
    # where the average_view variable is calculated in this dict comprehension.
    self.tag_summary = {
      tag:[val[0],val[1],round(float(val[1])/val[0],1)] for 
      tag,val in self.tag_summary.items()}

  # End of __init__() # 

  def GetNumberOfPosts(self):
    """Return the number of posts in the archive."""

    return len(self.all_posts)


  def PrintTopTags(self, sort_var, N=10):
    """
    Print top N (default 10) tags, sorted by:
        0: Cumulative number of uses
        1: Cumulative number of views
        2: Average number of views per use

    For sorting based on the average, require a minimum number of views (20).
    """
    
    sortname = {0:'uses',1:'views',2:'average'}
    print 'Top {0} tags based on {1}:'.format(N, sortname[sort_var])
    print '{0:<4}\t{1:<18}\t{2:>5}'.format(
        'Rank', 'Tag', sortname[sort_var].upper())

    # If sorting based on the average, use a dictionary comprehension to 
    # filter out tags below minimum view count (20).
    min_views = 20 if sort_var == 2 else 0
    tags = {tag:[val[0],val[1],val[2]] for 
      tag,val in self.tag_summary.items() if val[1] >= min_views}
    

    # Sort the dictionary based on the variable of interest and print the
    # top N results.
    sorted_user_list = sorted(
        tags.items(), key = lambda x: x[1][sort_var], reverse=True)
    for rank in range(N):
      print '#{0:<4}\t{1:<18}\t{2:>5}'.format(
          rank+1,sorted_user_list[rank][0], sorted_user_list[rank][1][sort_var])

  def PrintTopUsers(self, sort_var, N=10):
    """
    Print top N (default 10) users, sorted by:
      0: Total number of posts
      1: Cumulative post score
      2: Average post score
      
    """

    sortname = {0:'posts',1:'score',2:'average'}
    print 'Top {0} users based on {1}:'.format(N,sortname[sort_var])
    print '{0:<4}\t{1:<18}\t{2:>5}'.format(
        'Rank','UserID',sortname[sort_var].upper())

    # If sorting based on the average, use a dictionary comprehension to 
    # filter out users below a minimum number of posts (10).
    min_posts = 10 if sort_var == 2 else 0
    posts = {user_id:[val[0],val[1],val[2]] for 
      user_id,val in self.user_summary.items() if val[0] >= min_posts}

    sorted_user_list = sorted(
        posts.items(), key = lambda x: x[1][sort_var], reverse=True)
    for rank in range(N):
      print '#{0:<4}\t{1:<18}\t{2:>5}'.format(
          rank+1,sorted_user_list[rank][0], sorted_user_list[rank][1][sort_var])


  def PrintDateRange(self):
    """Print the first and last post dates, and approximate span in days."""

    print 'First post: {0}'.format(self.first_post_date)
    print 'Last post: {0}'.format(self.last_post_date)
    print 'Archive spans approximately {0} days, with {1} posts.'.format(
        (self.last_post_date - self.first_post_date).days, len(self.all_posts))

  def SaveTagDateData(self):
    """Save the tag and usage dates of tags to file for plotting routines.
       output file name has form: 
            ./<archive>/results/tag_date_data_<archive_name>.txt

       data file is stored in format where each row has a first entry equal
       to the tag name, and subsequent entries on that row are the date time
       stamps. The file is comma separated. The number of lines in the file 
       will equal the total number of tags used in the archive.

       A second file containing the tuples of the form (rank,tag_name,count)
       is created and stored as:
            ./<archive>/results/tag_rank_data_<archive_name>.txt
    """

    # Create date interpreter format and output file path. The root of the
    # archive name (<root>.stackexchange.com) will be used.
    date_format = "%Y-%m-%dT%H:%M:%S.%f"
    root = self.archive.split('.')[0]
    output_file = os.path.join(
        self.archive, 'results', 'tag_date_data_{0}.txt'.format(root))
    
    # Create tag date data output file.
    with open(output_file,'w') as output:
      # Form new dictionary with tags as keys and empty list as value
      tag_dates = {tag:[] for tag in self.tag_summary.keys()} 

      # Iterate over posts to extract use dates associated with each tag.
      for post in self.all_posts:
        date = post.GetCreationDate().strftime(date_format)
        for tag in post.GetTags():
          tag_dates[tag].append(date)

      # Write tag and date info to file for plotting routines to handle.
      for tag,dates in tag_dates.items():
        output.write(tag+','+','.join(dates)+'\n')

    # Create tag rank output file
    output_file = os.path.join(
        self.archive, 'results', 'tag_rank_data_{0}.txt'.format(root))
    with open(output_file,'w') as output:
      sorted_tag_ranks = sorted(
          self.tag_summary.items(), key = lambda x: x[1][0], reverse=True)
#         # x = {tag:(count,views,avg),...}, x[1][0] sorts on tag count
      for rank in range(len(sorted_tag_ranks)):
        output.write('{0},{1},{2}\n'.format(
          rank+1,sorted_tag_ranks[rank][0],sorted_tag_ranks[rank][1][0]))
