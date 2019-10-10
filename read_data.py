#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 21:14:24 2019

@author: giacomo
"""

import pandas as pd
import os
import datetime
import math

       
def Readtxt(folder):
    
    l_files=[]
    l_root=[]
    
    for root, dirs, files in os.walk(folder):
        l_root.append(root)
        l_files.append(files)
    d=[]
    
    for i in range(0,len(l_root)):
        root=l_root[i]
        
        for file in l_files[i]:
            if (file[-6:-4]!="_l") or (file[-6:-4]!="_L"):
                path=root+"/"+file
                f = open(path,"r")
                l_rows=f.readlines()
                f.close()
                
            tube_name=l_rows[1].split()[1]
            date_installation=l_rows[4].split()[4]
            
            # find '\n' rows in l_rows and find first line of last measurement
            l_i=[]
            for i in range(0,len(l_rows)):
                if l_rows[i]=="\n":
                    l_i.append(i)
            zero_row=l_i[-1]
                
            # check report type
            # report type 1: Prof.[m],Risultante[mm],Azimut[gradi]
            if len(l_rows[9])==42:

                date_misu_str=l_rows[zero_row+2].split()[2]
                date_misu=datetime.datetime.strptime(date_misu_str, "%d/%m/%Y").date()

                for i in range(zero_row+5,len(l_rows)):
                    row=l_rows[i].split()
                    # replacing , with . for str to float conversion
                    depth=float(row[0].replace(",","."))
                    ris=float(row[1].replace(",","."))
                    alpha=float(row[2].replace(",","."))
                    alpha_rad=math.radians(alpha)
                    E_disp=ris*math.cos(alpha_rad)
                    N_disp=ris*math.sin(alpha_rad)
                    
                    d.append({"tube_name":tube_name,"date":date_misu,"depth":depth,"E_disp":E_disp,"N_disp":N_disp,"resultant":ris,"angle":alpha})
            
            # report type 2: Prof.[m],Spost.Est[mm],Spost.Nord[mm],Risultante[mm],Azimut[gradi]  
            else:
                # find '\n' rows in l_rows and find first line of last measurement                
                date_misu_str=l_rows[zero_row+2].split()[2]
                date_misu=datetime.datetime.strptime(date_misu_str, "%d/%m/%Y").date()
                
                for i in range(zero_row+5,len(l_rows)):
                    row=l_rows[i].split()
                    # replacing , with . for str to float conversion
                    depth=float(row[0].replace(",","."))
                    E_disp=float(row[1].replace(",","."))
                    N_disp=float(row[2].replace(",","."))
                    ris=float(row[3].replace(",","."))
                    alpha=float(row[4].replace(",","."))

                    d.append({"tube_name":tube_name,"date":date_misu,"depth":depth,"E_disp":E_disp,"N_disp":N_disp,"resultant":ris,"angle":alpha})
                    
    df_meas_data= pd.DataFrame(d)
    df_meas_data=df_meas_data.set_index("tube_name")
    
    return(df_meas_data)

def ReadXLS(folder):
    
    l_files=[]
    d=[]
    for file in os.listdir(folder):
        l_files.append(file)
    
    for file_name in l_files:
    
        # read integrated measures sheetname from DataFrame 
        xl=pd.ExcelFile(folder+'/'+file_name)
        sheet_names=xl.sheet_names
        sheet_name_int=[sn for sn in sheet_names if "Diff.int" in sn]
        sheet_data=pd.read_excel(folder+'/'+file_name, sheet_name=sheet_name_int[0])
    
        # read general information
        tube_name=sheet_data.iloc[1,4]
        date_installation=sheet_data.iloc[8,8]
        #date_installation_str=sheet_data.iloc[8,8]
        #date_installation=datetime.datetime.strptime(date_installation_str, "%d/%m/%Y").date()
        date_misu_raw=sheet_data.iloc[3,4]

        if type(date_misu_raw)==pd._libs.tslibs.timestamps.Timestamp:
            date_misu=date_misu_raw.date()
        else:
            date_misu=datetime.datetime.strptime(date_misu_raw, "%d/%m/%Y").date()
        
        # clean raw_incl_data DataFrame from rows and columns with Nan values
        raw_incl_data=sheet_data.iloc[11::]
        raw_incl_data=raw_incl_data.dropna(axis=1, how='all')
        raw_incl_data=raw_incl_data.dropna(axis=0, how='any')
        raw_incl_data=raw_incl_data.set_index('AUSTRADA')
        # find row which contains columns names 
        ind_col_names=[ind for ind in raw_incl_data.index.tolist() if type(ind)==str]
        raw_col_names=raw_incl_data.loc[ind_col_names].values.tolist()
        # remove whitespaces from columns names
        col_names=[]
        for col_name in raw_col_names[0]:
            col_names.append(col_name.replace(" ", ""))
        raw_incl_data.columns=col_names
        # remove rows with non-number elements
        name_row_to_drop=[ind for ind in raw_incl_data.index.tolist() if type(ind)==str]
        raw_incl_data = raw_incl_data.drop(name_row_to_drop)
        # change data type from str to numeric
        for col_name in raw_incl_data:
            raw_incl_data[col_name]=pd.to_numeric(raw_incl_data[col_name])
    
        # calculate displacement components
        E_disp=[]
        N_disp=[]
        
        for i in range(0,len(raw_incl_data['RISULTANTE(mm)'])):
            E_disp=raw_incl_data['RISULTANTE(mm)'].iloc[i]*math.cos(raw_incl_data['AZIMUT(°)'].iloc[i])
            N_disp=raw_incl_data['RISULTANTE(mm)'].iloc[i]*math.sin(raw_incl_data['AZIMUT(°)'].iloc[i])
        
            d.append({"tube_name":tube_name,"date":date_misu,
                      "depth":raw_incl_data["PROFONDITA'dap.c.(m)"].iloc[i],
                      "E_disp":E_disp,"N_disp":N_disp,
                      "resultant":raw_incl_data["RISULTANTE(mm)"].iloc[i],
                      "angle":raw_incl_data["AZIMUT(°)"].iloc[i]})

    df_meas_data= pd.DataFrame(d)
    df_meas_data=df_meas_data.set_index("tube_name")
    
    return(df_meas_data)

def main():
    folder="./inclinometri_vds"
    df_meas=Readtxt(folder)
    #df_meas=ReadXLS(folder)
    
# call the main function
if __name__ == "__main__":
    main()

