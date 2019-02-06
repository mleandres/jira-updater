import datetime

def logM(s):
  pre = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')}: "
  m = pre + str(s)
  print(m)

def log(s):
  pre = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: "
  m = pre + str(s)
  with open("logs/connections_log", mode="a") as f:
    f.write(m + "\n")
  print(m)
