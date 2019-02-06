import sys
import re
from jira_api import get_issues_by_fixversion, get_all_subtasks, replace_fixversions, make_jira_req
from logger import log

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Error: Not enough arguments")
    print(f"Usage: python {sys.argv[0]} <fixVersion>")
    exit(1)

  fv = sys.argv[1]
  fv_pattern = r"^[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]$"
  if re.match(fv_pattern, fv) is None:
    print("Error: incorrect format. Try something like 12.14.00")
    exit(1)

  fields = ["subtasks"]
  issues = get_issues_by_fixversion(fv, fields)
  if len(issues) > 0:
    replace_fixversions(get_all_subtasks(issues), fv)
  