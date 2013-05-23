#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
"""Python module for sighis

Features:
- commandline interface for working with github issues
"""

__author__ = 'Steen Manniche <steen@manniche.net>'
__date__ = 'Tue May 21 22:16:49 2013'
__version__ = '$Revision:$'

prg_descr = """
SImple GitHub ISsues - See README.md for detailed usage and prerequisites
"""

import os, sys
import io
import re
import github3 as gh

abs_path_to_config = '.git/config'

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
        sys.exit( 'ERROR: no github username found, please refer to README.md, or try -u' )
        
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
        sys.exit( 'ERROR: no github token found, please refer to README.md' )

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

def auth( user, tkn ):
    """Authenticates with github
    
    Arguments:
    - `user`:
    - `tkn`:
    """
    ghlogin = gh.login( token=tkn )
    #ghlogin = gh.login( username=user, password='immanuelkant' )
    #ghlogin.check_authorization( ghlogin.token )
    #print( dir( ghlogin ) )
    return ghlogin

def search_issues( ghobj, repos_name, repos_owner, search_string ):
    """
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
    ghobj = auth( user, token )
    

    issues = []
    if lookup[0] is 'number':
        issues = find_issues( ghobj, repos_owner, repos_name, [ lookup[1] ] )
    elif lookup[0] is 'range':
        issues = find_issues( ghobj, repos_owner, repos_name, lookup[1] )
    elif lookup[0] is 'string':
        sys.exit( 'searching is currently not supported' )
        issues = search_issues( ghobj, repos_owner, repos_name, lookup[1] )

    print issues
    for i in issues:
        issue = i
        print( issue.title )
        print( issue.body )
        print( issue.comments )
        print( issue.user )
        print( issue.to_json() )
        
