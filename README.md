![lwdb logo](./.github/logo.png)

# LWDb: A centralized database of labware definitions

_Like that one movie database, but for labware._

This library provides a centralized database of labware definitions for use in lab automation software. It includes both a server and a client library. In addition, it provides tools for parsing VENUS labware definition files and converting them to the format used by this library.

## Consensus mechanism

The consensus mechanism is a simple majority voting system. The voters are users of this API who upload their labware definitions to the repository. Each user can only upload a definition for a given labware once (identified by a labware's name). If a user reuploads a definition, it will replace their previous submission. Between users, each upload is saved and organized by labware name. The definition with the most votes is the one that is used by the API.

## Python API

The Python API provides a simple wrapper around the HTTP API, as well as several utility scripts for uploading and downloading labware in bulk.

The API is available as `lwdb`.

```python
>>> import lwdb
>>> client = lwdb.Client(
...   base_url="https://lwdb.pylabrobot.org",
...   cache_dir="~/.lwdb")
```

### Installation

- pip

```bash
pip install lwdb
```

- source

```bash
git clone https://github.com/pylabrobot/lwdb
cd lwdb
pip install -e .
```

### Logging in

**Logging in is only required if you want to upload labware definitions.** If you don't have an account, you can create one [here](https://lwdb.pylabrobot.org/register).

```sh
python -m lwdb login
```

or

```python
>>> client.login(email="email@email.com", password="password")
```

### Registering an account

```sh
python -m lwdb register
```

### Uploading all labware definitions

```sh
python -m lwdb upload
```

### Downloading all labware definitions for offline use

```sh
python -m lwdb download
```

### Purging all labware definitions from cache

```sh
python -m lwdb purge
```

### Getting labware definition at runtime

```python
>>> labware = lwdb.get_labware('HTF_L')
```

### Uploading a labware definition

```python
>>> lwdb.upload_labware("name", {"data": "data"})
```

## HTTP API

The labware library is available as a HTTP API. The API is available at
`https://lwdb.pylabrobot.com/` and the API documentation is available at
`https://lwdb.pylabrobot.com/docs`.

### Get a labware definition

`GET` `/api/v1/labware/{labware_name}`: Get a labware resource.

- `200 OK`:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "name": "opentrons_96_tiprack_300ul",
  "definition": {
    "size_x": 100,
    "size_y": 100,
    "size_z": 100
  },
  "manufacturer": "That Company",
  "created_on": "2020-11-07T00:00:00.000000",
  "updated_on": "2020-11-07T00:00:00.000000"
}
```

- `404 Not Found`: The labware resource was not found.

### Getting all definitions

`GET` `/api/v1/labware?page=<int>`: Get all labware resources.

- `200 OK`:

```json
{
  "labware": [
    {
      "id": "00000000-0000-0000-0000-000000000000",
      "name": "company_96_tiprack_300ul",
      "definition": {
        "size_x": 100,
        "size_y": 100,
        "size_z": 100
      },
      "manufacturer": "That Company",
      "created_on": "2020-11-07T00:00:00.000000",
      "updated_on": "2020-11-07T00:00:00.000000"
    }
  ],
  "has_next": false
}
```

### Creating a labware definition

`POST` `/api/v1/labware`: Create a labware resource.

```json
{
  "name": "company_96_tiprack_300ul",
  "definition": {
    "size_x": 100,
    "size_y": 100,
    "size_z": 100
  },
  "manufacturer": "That Company"
}
```

- `201 Created`:

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "name": "company_96_tiprack_300ul",
  "definition": {
    "size_x": 100,
    "size_y": 100,
    "size_z": 100
  },
  "manufacturer": "That Company",
  "created_on": "2020-11-07T00:00:00.000000",
  "updated_on": "2020-11-07T00:00:00.000000"
}
```

### Logging in

`POST` `/api/v1/login`: Log in to the API.

- `200 OK`:

A cookie will be set in the response. This cookie serves as a session token for future requests.

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "email": "test@example.com",
  "created_on": "2020-11-07T00:00:00.000000",
  "updated_on": "2020-11-07T00:00:00.000000"
}
```

- `401 Unauthorized`: The email or password was incorrect.
