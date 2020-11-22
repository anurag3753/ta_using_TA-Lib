#!/bin/bash
source activate ta
cd /home/anurag/ta_using_TA-Lib
git clean -dffx
git reset --hard HEAD~5
git pull
/home/anurag/anaconda3/envs/ta/bin/python stock_quotes.py > stocks_analyze.txt
sleep 5m
python send_mail.py
cd -
