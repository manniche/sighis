#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-

__author__ = 'Steen Manniche <steen@manniche.net>'
__date__ = 'Tue May 21 22:16:49 2013'
__version__ = '$Revision:$'

prg_descr = """
SImple GitHub ISsues - See README.md for detailed usage and prerequisites

Features:
- commandline interface for working with github issues
"""

import os, sys
import io
import re
import github3 as gh
from github3.models import GitHubError

abs_path_to_config = '.git/config'
GREEN = '\033[92m'
HEADER = '\033[95m'
BLUE = '\033[94m'
WARNING = '\033[93m'
FAIL = '\033[91m'
RESET = '\033[0m'

def __check_path():
    """
    """
    if not os.path.exists( abs_path_to_config ):
        raise AssertionError( 'No git config file found at '+abs_path_to_config )

def __get_repo():
    """
    """
    with open( abs_path_to_config ) as gitconf:
        conf = gitconf.read().replace( '\t', '' )
        cp = ConfigParser.ConfigParser()
        cp.readfp(io.BytesIO( conf ) )
        try:
            url = cp.get( 'remote "origin"', 'url' )
            if url.startswith( 'git@' ):
                return url.rsplit( ':' )[1]
            elif url.startswith( 'https' ):
                return url.rsplit( '.com/' )[1]
            elif url.startswith( 'git://' ):
                return url.rsplit( '.com/' )[1]
        except ( ConfigParser.NoSectionError, ConfigParser.NoOptionError ) as e:
            pass

def __get_user( args ):
    user = None
    with open( abs_path_to_config ) as gitconf:
        conf = gitconf.read().replace( '\t', '' )
        cp = ConfigParser.ConfigParser()
        cp.readfp(io.BytesIO( conf ) )
        try:
            return cp.get( 'github', 'user' )
        except ( ConfigParser.NoSectionError, ConfigParser.NoOptionError ) as e:
            pass
    user = user or os.environ.get( 'GITHUB_USER' ) or args.user

    if not user:
        parser.print_help()
        sys.stderr.write('')
        sys.exit( '{0}ERROR:{1} no github username found, please refer to the README, or try -u'.format( RED, RESET ) )
        
    return user

def __get_token():
    token = None
    with open( abs_path_to_config ) as gitconf:
        conf = gitconf.read().replace( '\t', '' )
        cp = ConfigParser.ConfigParser()
        cp.readfp(io.BytesIO( conf ) )
        try:
            token = cp.get( 'github', 'token' )
        except ( ConfigParser.NoSectionError, ConfigParser.NoOptionError ) as e:
            pass

    token = token or os.environ.get( 'GITHUB_TOKEN' )

    if not token: 
        parser.print_help()
        sys.stderr.write('')
        sys.exit( '{0}ERROR{1}: no github token found, please refer to README.md'.format( RED, RESET ) )

    return token

def __parse_issue_string( issue_string ):
    """
    Warning: this function will not escape the string.

    >>> __parse_issue_string( '1' )
    ('number', 1)
    >>> __parse_issue_string( '1..5' )
    ('range', [1, 2, 3, 4, 5])
    >>> __parse_issue_string( '1-5' )
    ('range', [1, 2, 3, 4, 5])
    >>> __parse_issue_string( 'a4' )
    ('string', 'a4')
    >>> __parse_issue_string( '4a' )
    ('string', '4a')
    >>> __parse_issue_string( '4..a' )
    ('string', '4..a')
    >>> __parse_issue_string( '4-a' )
    ('string', '4-a')
    >>> __parse_issue_string( '4.a' )
    ('string', '4.a')
    >>> __parse_issue_string( '4--a' )
    ('string', '4--a')
    
    """
    try:
        return ( 'number', int( issue_string ) )
    except ValueError:
        pass

    if re.search( '^\d+\.\.\d+$', issue_string ) or re.search( '^\d+-\d+$', issue_string ):
        tu = re.split( '\.\.|-', issue_string )
        return ( 'range', range( int( tu[0] ), int( tu[1] )+1 ) )
        
    if type( issue_string ) is  str:
        return ( 'string', issue_string )

def auth( tkn ):
    """Authenticates with github using the provided token
    """
    try:
        ghlogin = gh.login( token=tkn )
    except GitHubError, e:
        sys.exit( '{0}ERROR{1}: when connecting to github: {2}'.format( RED, RESET, e ) )

    return ghlogin

def search_issues( ghobj, repos_name, repos_owner, search_string ):
    """Search for issues in the repository identified by `repos_name` using `search_string`
    """
    return ghobj.search_issues( repos_owner, repos_name, 'open', search_string )
   
def find_issues( ghobj, owner, repos, numbers ):
    """
    """
    issues = []
    for n in numbers:
        i = ghobj.issue( owner, repos, n )
        if i is not None:
            issues.append( i )

    return issues

    
if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import argparse    
    import ConfigParser
    parser = argparse.ArgumentParser( description=prg_descr )
    parser.add_argument( '-u', dest='user', type=str, nargs='?',
                         help='GitHub user name. If not provided by github.user or $GITHUB_USER, use this to give the program your github name' )
    parser.add_argument( dest='command', action='store', type=str,
                         help='')
    parser.add_argument( dest='issue', action="store", type=str,
                         help='%(prog)s looks in the context of the current project. %(prog)s will try to interpret this argument as a number first, a search string second. Please refer to README.md for a more thorough explanation.' )
    args = parser.parse_args()

    __check_path()
    repos_owner, repos_name = __get_repo().split( '/' )
    repos_name = repos_name.rsplit( '.' )[0]
    user  = __get_user( args )
    token = __get_token()
    lookup= __parse_issue_string( args.issue )
    ghobj = auth( token )
    

    issues = []
    if lookup[0] is 'number':
        issues = find_issues( ghobj, repos_owner, repos_name, [ lookup[1] ] )
    elif lookup[0] is 'range':
        issues = find_issues( ghobj, repos_owner, repos_name, lookup[1] )
    elif lookup[0] is 'string':
        #sys.exit( 'searching is currently not supported' )
        issues = search_issues( ghobj, repos_owner, repos_name, lookup[1] )

    MINW = 6*' '
    for i in issues:
        issue = i
        # d = dict( issue.to_json() )
        # print( d.keys() )
        print( '{0}Issue #{1}{width}{2}'.format( BLUE, RESET, i.number, width=MINW ) )
        print( '{0}Title{1}: {width}{2}'.format( BLUE, RESET, i.title, width=MINW ) )
        print( '{0}Description{1}:{width}{2}'.format( BLUE, RESET, i.body, width=' ' ) )
        print( '{0}Assigned to{1}:{width}{2}'.format( BLUE, RESET, i.assignee, width=' ' ) )
        print( '{0}Created by{1}:{width}{2}'.format( BLUE, RESET, i.user, width=2*' ' ) )
