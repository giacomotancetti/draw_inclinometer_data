#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 20:04:00 2018

@author: giacomo tancetti
"""
import pandas as pd
import ezdxf
  
# define list of all points names measured
def nomiIncl(df_meas):
    l_nomi_incl=df_meas.index.unique().tolist()
    l_nomi_incl.sort()
    return(l_nomi_incl)
        
# define list of all measure dates for each point
def DatesPerIncl(df_meas,l_nomi_incl):
    d_dates={}
    s_dates=set()
    
    for incl_name in l_nomi_incl:
        s_dates_i=set()
        s_dates_i.update(df_meas.loc[incl_name]["date"].tolist())
        d_dates[incl_name]=list(s_dates_i)
        s_dates.update(s_dates_i)
    l_dates=list(s_dates)
    return(d_dates,l_dates)

# creation of labels  
def DatesLabelsCreation(layer_name,i,text_h,drawing,modelspace):
    # insert point of dates labels
    x0=10
    y0=-20
    z0=0
    # vertical spacing of dates labels
    delta_y=text_h+(text_h/2)
    # insert point
    P_ins=(x0,y0-(delta_y*i),z0)
    modelspace.add_text(layer_name, dxfattribs={'layer': layer_name,'height': text_h}).set_pos(P_ins, align='CENTER')
  
# creation of scale bar  
def ScaleBarCreation(fs,text_h,drawing,modelspace):
    # lenght of 1 cm scalebar
    fs1=fs*10
    drawing.layers.new('scale_bar', dxfattribs={'color': 7})
    # insertion point of scale bar
    x0=10.
    y0=-20.
    z0=0.
    P0=(x0,y0,z0)
    P1=(x0,y0+(fs1/20.),z0)
    P2=((x0+fs1),y0,z0)
    P3=((x0+fs1),y0+(fs1/20.),z0)
       
    modelspace.add_line(P0,P1,dxfattribs={'layer': 'scale_bar'})   
    modelspace.add_line(P0,P2,dxfattribs={'layer': 'scale_bar'})    
    modelspace.add_line(P2,P3,dxfattribs={'layer': 'scale_bar'})    
    modelspace.add_text('0', dxfattribs={'layer': 'scale_bar','height': text_h}).set_pos(P1, align='CENTER')   
    modelspace.add_text('1 cm', dxfattribs={'layer': 'scale_bar','height': text_h}).set_pos(P3, align='BOTTOM_LEFT')

# creation of displacements arrows
def DrawDisp(drawing,d_dates,l_dates,df_meas,text_h,l_nomi_incl,pos_incl,fs,modelspace):
    
    j=1 # layer color index
    
    for i in range(1,len(l_dates)):
        l_dates_i_dt = pd.to_datetime(str(l_dates[i]))
        layer_name = l_dates_i_dt.strftime('%Y%m%d')
        drawing.layers.new(layer_name, dxfattribs={'color': j})
        j+=1
        DatesLabelsCreation(layer_name,i,text_h,drawing,modelspace)
    
    ScaleBarCreation(fs,text_h,drawing,modelspace)
    
    for nome_incl_i in pos_incl.keys():
        for date_i in d_dates[nome_incl_i]:
            delta_E=df_meas[df_meas['date']==date_i].loc[nome_incl_i]['E_disp'].to_list()
            delta_N=df_meas[df_meas['date']==date_i].loc[nome_incl_i]['N_disp'].to_list()
            depth=df_meas[df_meas['date']==date_i].loc[nome_incl_i]['depth'].to_list()
    
            for i in range(1,len(depth)):
                P0=(pos_incl[nome_incl_i][0]+fs*delta_E[i-1],pos_incl[nome_incl_i][1]+fs*delta_N[i-1],pos_incl[nome_incl_i][2]-depth[i-1])
                P1=(pos_incl[nome_incl_i][0]+fs*delta_E[i],pos_incl[nome_incl_i][1]+fs*delta_N[i],pos_incl[nome_incl_i][2]-depth[i])
                modelspace.add_line(P0, P1,dxfattribs={'layer': date_i.strftime('%Y%m%d')})
                
#------------------------------------------------------------------------------

def main():
    
    # height of text labels
    text_h=0.8
    # scale factor for dxf rappresentation
    fs=0.1

    l_nomi_incl=nomiIncl(df_meas)
    d_dates=DatesPerIncl(df_meas,l_nomi_incl)[0]
    l_dates=DatesPerIncl(df_meas,l_nomi_incl)[1]
    pos_incl={'n40':[0.0,0.0,0.0],'n41':[25.0,30.0,8.0],'n30':[-15.0,-30.0,-6.0]}

    # creation of dxf file of all dispacements
    drawing = ezdxf.new(dxfversion='R2010')
    modelspace = drawing.modelspace()
    DrawDisp(drawing,d_dates,l_dates,df_meas,text_h,l_nomi_incl,pos_incl,fs,modelspace)
    drawing.saveas('inclinometro.dxf')
    
# call the main function
if __name__ == "__main__":
    main()