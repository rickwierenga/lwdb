import json
import logging
import pickle
import os
from typing import Optional, Any
from urllib.parse import urljoin

import requests

logger = logging.getLogger("lwdb")


class APIError(Exception):
  """ LWDb API error """

  def __init__(self, resp):
    self.resp = resp
    try:
      self.message = resp.json()
      self.message = self.message["error"]
    except (json.decoder.JSONDecodeError, KeyError):
      self.message = resp.text

  def __str__(self):
    return self.message

  def __repr__(self):
    return f"APIError({self.message})"


class Client:
  """ LWDb API Client """

  def __init__(
    self,
    base_url: str = "https://lwdb.pylabrobot.org/",
    cache_dir: str = "~/.lwdb",
  ):
    self.base_url = base_url
    logger.debug("Using base url: %s", self.base_url)

    cache_dir = os.path.expanduser(cache_dir)
    self.cache_dir = cache_dir

    # Make sure the cache directory exists
    os.makedirs(self.cache_dir, exist_ok=True)

    # Get cookie file
    self.cookie_file = os.path.join(cache_dir, "cookies")
    logger.debug("Cookie file: %s", self.cookie_file)

    # Get labware dir
    self.labware_dir = os.path.join(cache_dir, "labware")
    os.makedirs(self.labware_dir, exist_ok=True)

    # Create a requests session, load cookies if they exist
    self.session = requests.session()
    try:
      with open(self.cookie_file, 'rb') as f:
        self.session.cookies.update(pickle.load(f))
        logger.debug("Loaded cookie")
    except FileNotFoundError:
      logger.info("No cookie file found, using anonymous mode")

  @property
  def _headers(self) -> dict:
    return {
      "Content-Type": "application/json",
      "Accept": "application/json",
    }

  def _save_definition(self, definition_name: str, data: dict):
    path = os.path.join(self.labware_dir, definition_name + ".json")
    with open(path, "w", encoding="utf-8") as f:
      data = json.dumps(data, indent=2)
      f.write(data)

  def _get_definition_cache(self, definition_name: str) -> Optional[dict]:
    path = os.path.join(self.labware_dir, definition_name + ".json")
    if not os.path.exists(path):
      return None
    with open(path, "r", encoding="utf-8") as f:
      data = json.load(f)
      return data

  def get(self, path: str, params: Optional[dict] = None) -> requests.Response:
    url = urljoin(self.base_url, path)
    logger.debug("GET %s %s", url, params)
    resp = self.session.get(url, params=params, headers=self._headers)
    if resp.status_code not in range(200, 299):
      raise APIError(resp)
    return resp

  def post(
    self,
    path: str,
    data: Optional[Any] = None,
    json: Optional[dict] = None # pylint: disable=redefined-outer-name
  ) -> requests.Response:
    url = urljoin(self.base_url, path)
    logger.debug("POST %s %s", url, json)
    resp = self.session.post(url, data=data, json=json, headers=self._headers)
    if resp.status_code not in range(200, 299):
      raise APIError(resp)
    return resp

  def login(self, username: str, password: str):
    response = self.post("/login", json={
      "email": username,
      "password": password
    })

    # Save the cookies
    with open(self.cookie_file, 'wb') as f:
      logger.info("Saving login cookie")
      pickle.dump(self.session.cookies, f)

    return response

  def logout(self):
    # just remove cache file
    try:
      os.remove(self.cookie_file)
    except FileNotFoundError:
      pass

  def get_labware(self, name: str, skip_cache: bool = False):
    if not skip_cache:
      cache = self._get_definition_cache(name)
      if cache is not None:
        logger.info("Using cached definition for %s", name)
        return cache

    url = urljoin("api/v1/labware/", name)
    resp = self.get(url)
    data = resp.json()

    self._save_definition(name, data)

    return data

  def upload_labware(self, name: str, definition: dict):
    resp = self.post("api/v1/labware", json={
      "name": name,
      "definition": definition
    })
    data = resp.json()
    return data

  def download_all(self):
    logger.info("downloading all...")

    page = 1
    while True:
      logger.info("Downloading page %d", page)

      resp = self.get("api/v1/labware", params={"page": page})
      data = resp.json()
      for labware in data["labware"]:
        self._save_definition(labware["name"], labware)

      if not data["has_next"]:
        break

      page += 1

  def upload_all(self):
    logger.info("uploading all...")

    raise NotImplementedError("Not implemented yet")
