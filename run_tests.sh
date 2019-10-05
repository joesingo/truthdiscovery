#!/bin/bash
dir=$(dirname $0)
coverage run --source truthdiscovery -m pytest ${dir}/truthdiscovery/test -v $*
coverage html
