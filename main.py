import os
from string import Template
import requests

import fastapi
from fastapi import staticfiles, Form, templating
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


GH_TOKEN = os.environ.get("GH_TOKEN")
BASE_URL = "https://api.github.com/graphql"
GRAPHQL_QUERY = """
query {
  user(login: "$username") {
    avatarUrl,
    repositories(first:1) {
      totalCount
    },
    contributionsCollection(
      from: "2023-01-01T00:00:00Z", to: "2023-12-31T23:59:00Z") {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""

def get_user_data(username: str) -> tuple | None:
  query = Template(GRAPHQL_QUERY).substitute(username=username)
  print(query)
  try:
    res = requests.post(BASE_URL, json={"query": f"{query}"},
      headers={
        "Authorization": f"bearer {GH_TOKEN}"
      })
    if res.status_code != 200 or not res:
      print("error: ", res.status_code)
      return None
    u = res.json()["data"]["user"]
    repos = u["repositories"]["totalCount"]
    contributions = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    icon = u["avatarUrl"]
    return contributions, repos, icon
  except Exception as e:
    print("exception", e)
    return None


app = fastapi.FastAPI()
app.mount("/static",
          staticfiles.StaticFiles(directory="static"), name="static")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

templates = templating.Jinja2Templates(directory="templates")


@app.get("/")
@limiter.limit("1/second")
async def index(request: fastapi.Request):
  return templates.TemplateResponse(
    "home/index.html", {"request": request})

@app.get("/share/{username}")
@limiter.limit("1/second")
async def share(request: fastapi.Request, username: str):
  if not (res := get_user_data(username)):
    raise fastapi.HTTPException(status_code=404, detail="User not found")
  contributions, repos, icon = res
  return templates.TemplateResponse(
    "share/index.html", {
      "request": request,
      "username": username,
      "contributions": contributions,
      "icon": icon,
      "repos": repos
    })

@app.get("/compute")
@limiter.limit("1/second")
async def compute(request: fastapi.Request):
  return templates.TemplateResponse("compute/form.html", {
    "request": request
  })

@app.post("/compute")
@limiter.limit("1/second")
def compute(request: fastapi.Request, username: str = Form(...)):

  if not (res := get_user_data(username)):
    return templates.TemplateResponse(
      "compute/form.html", {
        "request": request,
        "error": "User not found"
    })
  contributions, repos, icon = res
  return templates.TemplateResponse(
    "compute/results.html", {
      "request": request,
      "username": username,
      "contributions": contributions,
      "repos": repos,
      "icon": icon
  })
