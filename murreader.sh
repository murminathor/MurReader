#!/bin/sh

MUR_READER_PATH=./murreader
PYTHONPATH=${MUR_READER_PATH}/lib/python/:${MUR_READER_PATH}/lib/python/murreader ${MUR_READER_PATH}/bin/ob $@
