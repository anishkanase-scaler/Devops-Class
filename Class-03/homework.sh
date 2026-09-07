#!/bin/bash
mkdir homework
read -p "Enter your name: " name

curr_date=$(date)

touch homework>processes.txt
ps > homework/processes.txt
hostname=$(hostname)

echo "Hostname: $hostname"
echo "Hello, $name"
echo "Current date: $curr_date"

# disk_usage=$(df -h)
touch homework>diskusage.txt

df -h > homework/diskusage.txt
echo "Disk Usage:"
df -h > homework/diskusage.txt
cat homework/diskusage.txt