#!/bin/bash
base_dir="/home/joe/uni/project/repo/reports/"
log_file="${base_dir}/wc.csv"
count=$(find "${base_dir}/" -type f -name "*.tex" | xargs detex | wc -w)
timestamp=$(date +%s)
echo "$timestamp,$count" | tee -a "$log_file"
