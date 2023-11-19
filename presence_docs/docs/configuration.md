# Configuration

In order to run, you will need an ASGI server like Uvicorn, Hypercorn, or Daphne.
Since this app is not reliant on one or the other, I have not included one in
`dev-packages`. For ease, I would recommend uvicorn.

## Uvicorn

Uvicorn is an ASGI server for Python. It is pretty minimal and low-level, it is what
I use for myself. To run, all you need to do is install it.

### Installation

Run `pip install uvicorn` from within your environment.

### Running the server

#### Via CLI

* `uvicorn asgi:asgi_app --reload` - This will start the server. **asgi** points to
asgi.py and **asgi_app** points to the asgi_app variable within the file.

#### Programmatically

Uvicorn also allows programmatic running similar to a standard Flask app. In order to
do so will require altering of the `asgi.py` file. First you will need to `import uvicorn`.
