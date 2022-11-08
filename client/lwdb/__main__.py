import argparse
from getpass import getpass
import logging

import lwdb

def _get_string(prompt):
  data = input(prompt)
  if data == "":
    return _get_string(prompt)
  return data

def login(client):
  email = _get_string("Email: ")
  password = getpass("Password: ")

  try:
    client.login(email, password)
  except lwdb.client.APIError as e:
    print(f"Error: {e}")
    return
  print("Logged in as {}".format(email))

def logout(client):
  client.logout()
  print("Logged out")

def register(client):
  email = _get_string("Email: ")
  password = getpass("Password: ")

  try:
    client.register(email, password)
  except lwdb.client.APIError as e:
    print(f"Error: {e}")
    return

  print(f"Registered as {email}")
  print("Please verify your email address before logging in")

def download(client):
  client.download_all()

def upload(client):
  print("uploading all")
  client.upload_all()

def get_help():
  print("usage: lwdb [command] [options]")
  print()
  print("commands:")
  print("  login     Login to the LWDB")
  print("  logout    Logout of the LWDB")
  print("  register  Register a new account")
  print("  download  Download all labware")
  print("  upload    Upload all labware")
  print()
  print("options:")
  print("  --base-url  The base URL of the LWDB")
  print("  --log       The log level (debug, info, warning, error, critical)")


def main():
  parser = argparse.ArgumentParser(prog="lwdb")
  parser.add_argument("command", choices=["login", "logout", "register", "download", "upload", "help"])
  parser.add_argument("--base-url", default="https://lwdb.pylabrobot.org/")
  parser.add_argument("--log", default="warning")
  args = parser.parse_args()

  # Get log level
  log_level = args.log
  numeric_level = getattr(logging, log_level.upper(), None)
  if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {log_level}")
  logger = logging.getLogger("lwdb")
  logger.setLevel(numeric_level)

  client = lwdb.Client(base_url=args.base_url)

  if args.command == "login":
    login(client)
  elif args.command == "logout":
    logout(client)
  elif args.command == "register":
    register(client)
  elif args.command == "download":
    download(client)
  elif args.command == "upload":
    upload(client)
  elif args.command == "help":
    get_help()
