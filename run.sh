#!/bin/bash
source activate ta
cd /home/anurag/ta_using_TA-Lib
/home/anurag/anaconda3/envs/ta/bin/python recommend.py > stocks_analyze.txt
python send_mail.py
cd -
