#%%

# -*- coding: utf-8 -*-
"""
Created on Mon Jan  7 11:07:46 2019

@author: bcubrich
"""

import pandas as pd
import numpy as np       
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

#this is a little lazy, but duplicated to ask user to enter 1hr data
def get_dat2():
    root = Tk()
    root.withdraw()
    root.focus_force()
    root.attributes("-topmost", True)      #makes the dialog appear on top
    filename = askopenfilename(title = "Select 1hr Avg Data")      # Open single file
    root.destroy()
    return filename

###############################################################################
#                                                                             #
#                                  Initialize                                 #
#                                                                             #
###############################################################################



site_text="""index,SITE NAME,Site Symbol,State Code,County Code,Site Code,Parameter,Analyt,POC,Method,Unit
7,Copperview,CV,49,035,2005,42401,SO2,2,100,007
8,Hawthorne,HW,49,035,3006,42401,SO2,2,560,008
9,Rose Park,RP,49,035,3010,42401,SO2,2,100,007
8,Magna,MG,49,035,1001,42401,SO2,2,560,007"""



unused="""0,Brigham City,BR,49,003,0003,42401,SO2,2,560,007
1,Smithfield,SM,49,005,0007,42401,SO2,2,560,007
2,Price #2,P2,49,007,1003,42401,SO2,2,560,007
3,Bountiful #2,BV,49,011,0004,42401,SO2,2,560,007
4,Roosevelt,RS,49,013,0002,,,2,000,000
5,Escalante,ES,49,017,0006,42401,SO2,2,560,007
6,Enoch,EN,49,021,0005,42401,SO2,2,560,007
10,Herriman,H3,49,035,3013,42401,SO2,2,560,007
11,Erda,ED,49,045,0004,42401,SO2,2,560,007
12,Vernal,V4,49,560,1004,42401,SO2,2,560,007
13,Lindon,LN,49,049,4001,42401,SO2,2,560,007
14,Spanish Fork,SF,49,049,5010,42401,SO2,2,560,007
15,Ogden,O2,49,057,0002,42401,SO2,2,560,007
16,Harrisville,HV,49,057,1003,42401,SO2,2,560,007
17,Hurricane,HC,49,053,0007,42401,SO2,2,560,007
18,Antelope Island,AI,49,011,6001,42401,SO2,2,560,012
19,Saltair,SA,49,035,3005,42401, SO2,2,560,012"""


sites_df=pd.DataFrame()
#df_dict=dict()
for line in site_text.split('\n'):
    temp_df=pd.DataFrame(line.split(',')).T
    sites_df=sites_df.append(temp_df)
#    temp=line.split(',')
#    df_dict[temp[0]]=temp[1:]
    
sites_df=sites_df.set_index(0)
sites_df.columns=sites_df.loc['index',:]
sites_df=sites_df.drop('index', axis='index')


#%%

###############################################################################
#                                                                             #
#                                  GUI                                        #
#                                                                             #
###############################################################################

so2_5min_file=get_dat()   #get 5min data path
so2_1hr_file=get_dat2()   #get 1 hr data path

#%%


master = Tk()
master.attributes("-topmost", True)      #makes the dialog appear on top

#create the variable to hold the dropdown value
variable1 = StringVar(master)

#set dropdown default value
variable1.set("HW") 

#create dropdown. Each text item is an entry in the dropdown. Positional variable
#1 gives the tk window to use, and pos 2 give the variable to hold dropdown value
w = OptionMenu(master, variable1, *sites_df['Site Symbol'].values)
w.grid(row=1, sticky=W, column=0)

#when the user presses okay get the final value of the drpodown
def quit():
    global choice
    #this is the variable we wanted from the user
    choice=variable1.get()
    master.destroy()

#it's best to have the code wait for the user to press okay to move on. 
#This prevents having to check if the state of the window has changed.
button = Button(master, text="OK", command=quit)
button.grid(row=1, sticky=W, column=2)

labelText=StringVar()
labelText.set("Select Site")
label1=Label(master, textvariable=labelText, height=4)
label1.grid(row=0, column=0, columnspan=2)



#final variable we wanted to keep here is 'choice'


mainloop()

sites_df=sites_df[sites_df['Site Symbol']==choice]

#%%

###############################################################################
#                                                                             #
#                                  AirVision Style                            #
#                                                                             #
###############################################################################


aqs_file=so2_5min_file.split('.')[0]+'_aqs_nulled.txt' #path of AQS output of this py
av_file=so2_5min_file.split('.')[0]+'_av_nulled.csv'   #path of AirVision output
#out_file=so2_5min_file[:-4]+'_nulled.txt'

#create dfs out of file paths
so2_5min=pd.read_excel(so2_5min_file, dtype=str)
so2_1hr=pd.read_excel(so2_1hr_file, dtype=str)

#remember columns so that temporary columns can be dropped
av_columns=so2_5min.columns

###############################################################################
#next, need to drop the date/time column down so that only the hour is specified
#by dropping the 5 minute aspect a dictionary can be created to map values 
#from the hourly data to the 5minute data 
# # # # # # # # #  # # # # # # # # # # # ## # # # # # # ## # # # # # # # # # # 
so2_5min['dt']=so2_5min['Date'].str[:13]
so2_1hr['dt']=so2_1hr['Date'].str[:13]

#create dictionary to map AQS null codes from hourly to 5m data
code_dict=dict(zip(so2_1hr['dt'].values,so2_1hr['AQS Null Code'].values))

#map hourly nul codes to 5m daa
so2_5min['hr_code']=so2_5min['dt'].map(code_dict)

#check for missing null codes in 5m data. If missing check if it is present 
#in the hourly. Keeps 5 minute null codes, but adds null codes from hourly data.
so2_5min['AQS Null Code']=np.where(so2_5min['AQS Null Code'].str.contains('nan'),
        so2_5min['hr_code'],so2_5min['AQS Null Code'] )




###############################################################################
#                                                                             #
#                         Create AQS Output                                   #
#                                                                             #
###############################################################################

#need these columns to create empty df
columns_raw=r'Transaction Type|Action Indicator|State Code|County Code|Site '\
        r'Number|Parameter Code|POC|Duration|Unit|'\
        r'Method|Date|Time|Value|AQS Null Code|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18'

#need columns as list
columns=columns_raw.split('|')

#create a new df to handle to export to AQS
aqs_out=pd.DataFrame(columns=columns)   #want to initialize the df with the right columns
aqs_out['Value']=so2_5min['Value']
aqs_out['AQS Null Code']=so2_5min['AQS Null Code']
aqs_out['Value']=np.where(aqs_out['AQS Null Code'].str.contains('nan'),aqs_out['Value'],'nan')
aqs_out['Value']=np.where(aqs_out['Value'].str.contains('-'),'0',aqs_out['Value'])

#The following 12 lines handle getting the right AQS file upload parameters, using sites_df.
aqs_out['Transaction Type']='RD'
aqs_out['Action Indicator']='I'
aqs_out['State Code']='49'
aqs_out['County Code']=sites_df['County Code'].values[0]
aqs_out['Site Number']=sites_df['Site Code'].values[0]
aqs_out['Parameter Code']='42401'
aqs_out['POC']=sites_df['POC'].values[0]
aqs_out['Duration']='H'
aqs_out['Unit']=sites_df['Unit'].values[0]       
aqs_out['Method']=sites_df['Method'].values[0] 
aqs_out['Date']=(so2_5min['Date'].str[0:4]
       + so2_5min['Date'].str[5:7]
       + so2_5min['Date'].str[8:10])
aqs_out['Time']=so2_5min['Date'].str[11:16]
#%%
###############################################################################
#                                                                             #
#                           Warning Message                                   #
#                                                                             #
###############################################################################

if sites_df['Unit'].values[0] == '008':       #warnings for ppb instruments
    warning_level=20
    print('Warning, {} values exceed {}ppb. Please see "warning_df" for details'.format(len(aqs_out[aqs_out['Value'].astype(float)>=warning_level]),warning_level))
    waring_df=aqs_out[aqs_out['Value'].astype(float)>=warning_level].copy()
    waring_df['Value']=waring_df['Value'].astype(float)
    
elif sites_df['Unit'].values[0] == '007':      #warnings for ppm instruments
    warning_level=0.02
    print('Warning, {} values exceed {}ppm. Please see "warning_df" for details'.format(len(aqs_out[aqs_out['Value'].astype(float)>=warning_level]),warning_level))
    waring_df=aqs_out[aqs_out['Value'].astype(float)>=warning_level].copy()
    waring_df['Value']=waring_df['Value'].astype(float)
#    waring_df=waring_df[]


#%%
###############################################################################
#                                                                             #
#                  Create Air Vision Output                                   #
#                                                                             #
###############################################################################


flag_dict=dict(zip(so2_1hr['dt'].values,so2_1hr['Flags'].values))

so2_5min['hr_flag']=so2_5min['dt'].map(flag_dict)
so2_5min['Flags']=np.where(so2_5min['Flags'].str.contains('nan'),
        so2_5min['hr_flag'],
        so2_5min['Flags'])

av_out=so2_5min[av_columns].copy()
av_out['Parameter']='42401'
av_out['Value']=np.where(av_out['Value'].str.contains('-'),'0',av_out['Value'])
av_out['Raw Value']=np.where(av_out['Raw Value'].str.contains('-'),'0',av_out['Raw Value'])

av_out=av_out.replace(to_replace='nan', value=np.nan)
av_out=av_out.sort_values('Date')

av_out['Date']=av_out['Date'].str[5:7]+'/'+av_out['Date'].str[8:10]+'/'+av_out['Date'].str[0:4]+' '+av_out['Date'].str[11:16]



av_out=av_out.set_index('Site') #need to get rid of index
av_out.to_csv(av_file)


###############################################################################
#                                                                             #
#                              Write to file                                  #
#                                                                             #
###############################################################################
update=False
if update==True: aqs_out['Action Indicator']='U' 


aqs_out=aqs_out[columns].copy()
aqs_out=aqs_out.set_index('Transaction Type') #need to get rid of index
aqs_out=aqs_out.replace(to_replace='nan', value=np.nan)
aqs_out.to_csv(aqs_file, sep='|')



'''---------
The following whole bit is used to add a '#' to the first line of the file. 
Seems like a lot of code just to add a hashtag to the file, but I like having 
the header info right in the file, in case someone only sees the text file.
------'''
appendText='#'
text_file=open(aqs_file,'r')
text=text_file.read()
text_file.close()
text_file=open(aqs_file,'w')
text_file.seek(0,0)
text_file.write(appendText+text)
text_file.close()





