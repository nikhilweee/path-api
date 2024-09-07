# path-api

A python implementation of the PATH API.

Mainly intended to be a replacement for the public API available at
https://www.panynj.gov/bin/portauthority/ridepath.json

# Setup

Install dependencies using your favourite package manager.

```console
$ uv sync
```

# Usage

(One-time setup) Fetch the latest database.

```console
$ python path/db.py
```

Listen to SignalR Hubs for new messages.

```console
 $ python listen.py
```

Start a FastAPI server to serve data.

```console
 $ fastapi run api.py
```

The latest data should be available at http://localhost:8000/ridepath.json.

# References

1. Matt Razza's [API](https://github.com/mrazza/path-data) written in C#
1. Matt Razza's
   [blog post](https://medium.com/@mrazza/programmatic-path-real-time-arrival-data-5d0884ae1ad6)
   on Medium
1. [Public API](https://www.panynj.gov/bin/portauthority/ridepath.json) on
   panynj.gov
