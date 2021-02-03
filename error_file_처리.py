from hyperparam import *
from pdf_listed_comp import *
from 공정위 import *
import pandas as pd
import numpy as np
import re
import os
import csv
import sys



if __name__ =="__main__":
    err = pd.read_excel(clean_df + "err.xlsx")
    오류유형 = err.columns.tolist()
    추출오류 = err[오류유형[-1]].drop_duplicates().dropna()
    for file in 추출오류:
        a = pdf_처리(file)
        if (len(a) > 2000) :
            print(len(a), a[:100])
