#!/bin/bash
inputfile=$1
outfile=$2
date=$3

cd -
rm -rf ta_using_TA-Lib
git clone https://github.com/anurag3753/ta_using_TA-Lib.git
cd ta_using_TA-Lib
python recommend.py $1 $3 > $2
python send_mail.py
git add $2
git commit -m "update recommendation"
ssh -T git@github.com
git remote set-url origin git@github.com:anurag3753/ta_using_TA-Lib.git
git push
cd -
