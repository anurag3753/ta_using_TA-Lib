#!/bin/bash
source activate ta
cd /home/anurag/ta_using_TA-Lib
python stock_quotes.py > stocks_analyze.txt
sleep 5m
python send_mail.py
cd -