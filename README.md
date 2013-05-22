# sighis (SImple GitHub ISsue cli) #

A python cli for github issues

## Dependencies ##

+ The most approachable [github3.py](https://github.com/sigmavirus24/github3.py) from [Ian Cordasco](http://www.coglib.com/~icordasc/blog/).
  `pip install github3.py` or roll your own from the repository.
+ python2.7 or better.

## Usage ##

Get an auth token from your github account and either put it in `$GITHUB_TOKEN` environment variable or store it in your `myproject/.git/config` under github.token:

`git config github.token 1A2B3C4D5E6F7A8B9C0D`

sighis will look for the username of your github account with the following preferences:

1. `github.user` in `myproject/.git/config` 
2. `$USER`
3. `-u` parameter value to the program

### Issue lookup heuristics ###

sighis will try to interpret the positional argument given by the following heuristic:

1. Try to interpret the argument as an integer. If successful, a lookup will be made for the specific issue number
2. If the argument has the following form: `12..15` or `12-15`, the program will interpret the argument as a range of issue numbers, inclusive. If this is the case, a lookup will be made for the range of numbers and a list of issues will be returned
3. If the argument cannot be parsed to any of the two above forms, it will be interpreted as a search string and a search will be performed against all the issues in the project.
