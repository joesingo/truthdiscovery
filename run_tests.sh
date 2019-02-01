#!/bin/bash
dir=$(dirname $0)
coverage run -m pytest ${dir}/truthdiscovery/test
