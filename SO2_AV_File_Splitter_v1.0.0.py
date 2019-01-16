#%%
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 13:40:56 2019

@author: bcubrich
"""

import pandas as pd

from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import *


#ask user to specify 5 minute data
def get_dat():
    root = Tk()
    root.withdraw()
    root.focus_force()
    root.attributes("-topmost", True)      #makes the dialog appear on top
    filename = askopenfilename(title = "Select 5 Minute Data")      # Open single file
    root.destroy()
    return filename




filename=get_dat()


parse_df=pd.read_csv(filename, dtype=str)

number_of_files=6

files=[]
#length=0
for i in range(number_of_files):
    begin=int(i*len(parse_df)/number_of_files)
    end=int((i+1)*len(parse_df)/number_of_files)
    df=parse_df[begin:end]
#    length+=len(df)
    files.append(df)

i=0
for file in files:
    i+=1
    out_name=filename.split('.')[0]+'_'+str(i)+'of'+str(number_of_files)+'.csv'
    file=file.set_index(file.columns[0])
    file.to_csv(out_name)
    