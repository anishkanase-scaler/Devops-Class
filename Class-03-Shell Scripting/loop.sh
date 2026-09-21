#!/bin/bash

for ((i = 0; i<5; i++))
do
    echo "this is iteration number $i"
done
# prints 1 to 4


for i in {1..5}
do 
    echo "this is iteration number $i"
done 
# prints 1 to 5


# [] => is a condition/test
# (()) => tells bash that something written inside this should be treated as 
# math/arithmetic


