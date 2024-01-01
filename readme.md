# The Most Accurate GitHub Value Calculator
## AKA: Happy New Year! 2024
Just having some fun to find an excuse to see what HTMX is all about.

Based this on: https://github.com/marty331/fasthtmx - never used Jinja before
either so that's cool, seems just like Django templates.

I'm not sure why you would want to run this, but if you did:

```
pip install -r requirements.txt
uvicorn main:app --reload
```

You need a Personal Access Token from GitHub to make the GraphQL query work,
just give it no permissions other than read public info. The set the GH_TOKEN
env variable.

Then go to http://localhost:8000/ and check it out. 

PR's welcome if you would like to further the troll.
