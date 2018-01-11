#!/usr/bin/env bash
docker build --no-cache -t blockchain . && docker run --rm -p 80:5000 blockchain
