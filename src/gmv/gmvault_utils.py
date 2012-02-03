'''
Created on Dec 1, 2011

@author: guillaume.aubert@gmail.com
'''
import os

import re
import datetime
import calendar
import fnmatch
import functools

import StringIO
import sys
import traceback
import string
import random  

class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            value = self.func(*args)
            self.cache[args] = value
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__
    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
    

def make_password(minlength=8,maxlength=16):  
    """
       generate randomw password
    """
    length = random.randint(minlength,maxlength)
    letters = string.ascii_letters+string.digits # alphanumeric, upper and lowercase  
    return ''.join([random.choice(letters) for _ in range(length)])  



def get_exception_traceback():
    """
            return the exception traceback (stack info and so on) in a string
        
            Args:
               None
               
            Returns:
               return a string that contains the exception traceback
        
            Raises:
               
    """
   
    the_file = StringIO.StringIO()
    exception_type, exception_value, exception_traceback = sys.exc_info() #IGNORE:W0702
    traceback.print_exception(exception_type, exception_value, exception_traceback, file = the_file)
    return the_file.getvalue()

ZERO = datetime.timedelta(0) 

# A UTC class.    
class UTC(datetime.tzinfo):    
    """UTC Timezone"""    
    
    def utcoffset(self, a_dt):  
        ''' return utcoffset '''  
        return ZERO    
    
    def tzname(self, a_dt):
        ''' return tzname '''    
        return "UTC"    
        
    def dst(self, a_dt):  
        ''' return dst '''      
        return ZERO  

# pylint: enable-msg=W0613    
UTC_TZ = UTC()

def get_ym_from_datetime(a_datetime):
    """
       return year month from datetime
    """
    if a_datetime:
        return a_datetime.strftime('%Y-%m')
    
    return None

MONTH_CONV = { 1: 'Jan', 4: 'Apr', 6: 'Jun', 7: 'Jul', 10: 'Oct' , 12: 'Dec',
               2: 'Feb', 5: 'May', 8: 'Aug', 9: 'Sep', 11: 'Nov',
               3: 'Mar'}

REVERSE_MONTH_CONV = { 'Jan' : 1, 'Apr' : 4, 'Jun' : 6, 'Jul': 7, 'Oct': 10 , 'Dec':12,
                   'Feb' : 2, 'May' : 5, 'Aug' : 8, 'Sep': 9, 'Nov': 11,
                   'Mar' : 3}


MONTH_YEAR_PATTERN = r'(?P<year>(18|19|[2-5][0-9])\d\d)[-/.](?P<month>(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))'
MONTH_YEAR_RE = re.compile(MONTH_YEAR_PATTERN)

def compare_yymm_dir(first, second):
    """
       Compare directory names in the form of Year-Month
       Return 1 if first > second
              0 if equal
              -1 if second > first
    """
    
    matched = MONTH_YEAR_RE.match(first)
    
    if matched:
        first_year  = int(matched.group('year'))
        first_month = REVERSE_MONTH_CONV.get(matched.group('month'))
        
        first_val   = (first_year * 1000) + first_month
    else:
        raise Exception("Invalid Year-Month expression (%s). Please correct it" % (first))
        
    matched = MONTH_YEAR_RE.match(second)
    
    if matched:
        second_year  = int(matched.group('year'))
        second_month = REVERSE_MONTH_CONV.get(matched.group('month'))
        
        second_val   = (second_year * 1000) + second_month
    else:
        raise Exception("Invalid Year-Month expression (%s). Please correct it" % (second))
    
    if first_val > second_val:
        return 1
    elif first_val == second_val:
        return 0
    else:
        return -1
    
def get_all_directories_posterior_to(a_dir, dirs):
    """
           get all directories posterior
    """
    #sort the passed dirs list and return all dirs posterior to a_dir
         
    return [ name for name in sorted(dirs, key=functools.cmp_to_key(compare_yymm_dir))\
             if compare_yymm_dir(a_dir, name) <= 0 ]

def get_all_dirs_under(root_dir):
    """
       Get all directory names under (1 level only) the root dir
    """
    return [ name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name)) ]

def datetime2imapdate(a_datetime):
    """
       Transfrom in date format for IMAP Request
    """
    if a_datetime:
        
        month = MONTH_CONV[a_datetime.month]
        
        pattern = '%%d-%s-%%Y' %(month) 
        
        return a_datetime.strftime(pattern)
    

def e2datetime(a_epoch):
    """
        convert epoch time in datetime

            Args:
               a_epoch: the epoch time to convert

            Returns: a datetime
    """

    #utcfromtimestamp is not working properly with a decimals.
    # use floor to create the datetime
#    decim = decimal.Decimal('%s' % (a_epoch)).quantize(decimal.Decimal('.001'), rounding=decimal.ROUND_DOWN)

    new_date = datetime.datetime.utcfromtimestamp(a_epoch)

    return new_date

def datetime2e(a_date):
    """
        convert datetime in epoch
        Beware the datetime as to be in UTC otherwise you might have some surprises
            Args:
               a_date: the datertime to convert

            Returns: a epoch time
    """
    return calendar.timegm(a_date.timetuple())

def makedirs(aPath):
    """ my own version of makedir """
    
    if os.path.isdir(aPath):
        # it already exists so return
        return
    elif os.path.isfile(aPath):
        raise OSError("a file with the same name as the desired dir, '%s', already exists."%(aPath))

    os.makedirs(aPath)

def __rmgeneric(path, __func__):
    """ private function that is part of delete_all_under """
    try:
        __func__(path)
        #print 'Removed ', path
    except OSError, (errno, strerror): #IGNORE:W0612
        print """Error removing %(path)s, %(error)s """%{'path' : path, 'error': strerror }
            
def delete_all_under(path,delete_top_dir=False):
    """ delete all files and directories under path """

    if not os.path.isdir(path):
        return
    
    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            f=os.remove
            __rmgeneric(fullpath, f)
        elif os.path.isdir(fullpath):
            delete_all_under(fullpath)
            f=os.rmdir
            __rmgeneric(fullpath, f)
    
    if delete_top_dir:
        os.rmdir(path)
    
        
def dirwalk(a_dir, a_wildcards= '*'):
    """
     Walk a directory tree, using a generator.
     This implementation returns only the files in all the subdirectories.
     Beware, this is a generator.
     
     Args:
         a_dir: A root directory from where to list
         a_wildcards: Filtering wildcards a la unix
    """

    #iterate over files in the current dir
    for the_file in fnmatch.filter(sorted(os.listdir(a_dir)), a_wildcards):
        fullpath = os.path.join(a_dir, the_file)
        if not os.path.isdir(fullpath):
            yield fullpath
    
    sub_dirs = os.walk(a_dir).next()[1]
    #iterate over sub_dirs
    for sub_dir in sub_dirs:
        fullpath = os.path.join(a_dir, sub_dir)
        for p_elem in dirwalk(fullpath, a_wildcards):
            yield p_elem 
            
if __name__ == '__main__':
   
    print(get_all_directories_posterior_to('2011-Apr', ['2011-Mar', '2010-Feb', '2012-Mar', '2011-Apr', '2011-May']))
  