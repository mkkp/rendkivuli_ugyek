#!/usr/bin/env python3
from app import app
from app.env import DEBUG_MODE, PORT

if __name__ == "__main__":
    app.run(host="localhost", port=PORT, debug=DEBUG_MODE)
