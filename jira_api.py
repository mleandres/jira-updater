import json
from pprint import pprint
from requests_futures.sessions import FuturesSession
from logger import log

def make_jira_req(type="post", data = {}):
  if type == "post":
    return
  elif type == "put":
    return
  else:
    raise ValueError("Only 'post' and 'put' request types are supported")


# gets stories from jira project by specifying fix version and fields to return
# fixversion is required
# returns an array of the jira issue dicts with the requested fields (among others)
def get_issues_by_fixversion(fv, fields=[], 
  search_url="http://cavcops01:9081/rest/api/2/search",
  username="redacted.username", password="redacted.password"):
  log("Connecting to Jira API...")

  session = FuturesSession()
  headers = {"content-type": "application/json"}

  data_dict = { 
    "jql": f"fixversion = {fv} AND type != Sub-task ORDER BY key ASC",
    "maxResults": 1000,
    "fields": fields
  }
  data_json = json.dumps(data_dict)

  if len(fields) == 0:
    fields = "all"
  log(f"Making request with JQL = ' {data_dict['jql']} ' for fields {fields}")

  search_future = session.post(
    search_url, 
    data_json, 
    auth=(username, password), 
    headers=headers
  )
  search_resp = search_future.result()
  
  issues = []
  if search_resp.status_code < 300:
    issues = search_resp.json()["issues"]
    log(f"Found {len(issues)} Jira issue{'' if len(issues) == 1 else 's'}")
  else:
    log(f"Error occured while searching Jira")
    log(f"\tResponse Status Code: {search_resp.status_code}")
    log(f"\tError: {search_resp.text}")
  
  return issues


# gets a list of sub-tasks from a story dict if that key exists
# gets only specified fields and defaults to all
def get_subtasks(issue, fields=["id","key"]):

  log(f"Getting subtasks for {issue['key']}")

  issue = issue["fields"]
  if ("subtasks" in issue) and (len(issue["subtasks"]) > 0):
    subtasks = issue["subtasks"]
    res = []

    for st in subtasks:
      log(f"Found {st['key']}")

      d = {}
      if len(fields) > 0:
        for f in fields:
          if f in st.keys():
            d[f] = st[f]
          else:
            log(f"Field '{f}' not found in subtask {st['key']}")

      else:
        d = st

      res.append(d)
    return res

  log("No subtasks found")
  return []


## given a list of issues, produces a list of all subtasks from those issues
## can specify what fields
def get_all_subtasks(issues, fields=["id", "key"]):
  subtasks = []
  for i in issues:
    subtasks += get_subtasks(i, fields)
  return subtasks


# replaces the fixversion of a single issue
# returns 0 if successful, 1 if unsuccessful
def replace_fixversion(issue, fv,
  search_url="http://cavcops01:9081/rest/api/2/issue/",
  username="mathew.leandres", password="Validus18"):

  session = FuturesSession()
  headers = {"content-type": "application/json"}
  status = 1

  # format required for jira API
  data_dict = {"fields": {"fixVersions": [{"name": fv}]}}
  data_json = json.dumps(data_dict)

  log(f"Attempting to update {issue['key']} to fixVersion {fv}")

  update_future = session.put(
    search_url + issue["key"],
    data=data_json,
    auth=(username, password),
    headers=headers
  )
  update_result = update_future.result()
  if (update_result.status_code < 300):
    log(f"Successfully updated {issue['key']} to fixVersion {fv}")
    status = 0
  else:
    log(f"Warning: Could not update {issue['key']} to fixVersion {fv}")
    log(f"\tStatus Code: {update_result.status_code}")
    log(f"\tError: {update_result.text}")
    status = 1
  return status

  
# replaces fixversions for a list of issues
# returns 0 if no issues, otherwise, returns the number unsuccessful attempts
def replace_fixversions(issues, fv):
  errors = 0

  for i in issues:
    errors += replace_fixversion(i, fv)

  log(f"{errors} errors reported")
  return errors
