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
import re

def __get_user( args ):
    user = None
    with open( '.git/config' ) as gitconf:
        conf = gitconf.read().replace( '\t', '' )
        cp = ConfigParser.ConfigParser()
        cp.readfp(io.BytesIO( conf ) )
        try:
            return cp.get( 'github', 'user' )
        except ( ConfigParser.NoSectionError, ConfigParser.NoOptionError ) as e:
            pass
    return user or os.environ.get( 'GITHUB_USER' ) or args.user

def __get_token():
    token = None
    with open( '.git/config' ) as gitconf:
        conf = gitconf.read().replace( '\t', '' )
        cp = ConfigParser.ConfigParser()
        cp.readfp(io.BytesIO( conf ) )
        try:
            token = cp.get( 'github', 'token' )
        except ( ConfigParser.NoSectionError, ConfigParser.NoOptionError ) as e:
            pass
    return token or os.environ.get( 'GITHUB_TOKEN' )

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

def find_issue( issue_type, lookup ):
    """
    
    Arguments:
    - `issue_type`:
    - `lookup`:
    """
    pass

    
if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import argparse    
    import ConfigParser
    import io
    parser = argparse.ArgumentParser( description=prg_descr )
    parser.add_argument( '-u', dest='user', type=str, nargs='?',
                         help='GitHub user name. If not provided by github.user or $GITHUB_USER, use this to give the program your github name' )
    parser.add_argument( dest='issue', action="store", type=str,
                         help='%(prog)s looks in the context of the current project. %(prog)s will try to interpret this argument as a number first, a search string second. Please refer to README.md for a more thorough explanation.' )
    args = parser.parse_args()
    user = __get_user( args )
    token = __get_token()

    if not user:
        parser.print_help()
        print('')
        sys.exit( 'ERROR: no github username found, please refer to README.md, or try -u' )
        
    if not token: 
        parser.print_help()
        print('')
        sys.exit( 'ERROR: no github token found, please refer to README.md' )
        
    issue = __parse_issue_string( args.issue )

    find_issue( issue[0], issue[1] )
    
