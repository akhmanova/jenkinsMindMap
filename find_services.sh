#!/usr/bin/env bash

DIR=$(pwd)
cd "./output"
echo "FOUND INFO" > $DIR/found_info
echo "~~~~~~~~~~" >> $DIR/found_info
for dir in $(ls)
do
    cd $dir
    echo "SERVICE_BUILD $dir" >> $DIR/found_info
    RESULT=$(grep -C 4 $(cat service) ./output)
    echo ${RESULT}
    echo ${RESULT} >> $DIR/found_info
    cd ..

    echo "~~~~~~~~~~" >> $DIR/found_info
done

cd ..
rm -rf output_*
rm -rf output.csv
git add output* output.csv

git add found_info
git commit -m "from find_services.sh"
git push -f origin master