from bokeh.charts import Bar, output_file, show
from bokeh.charts.attributes import ColorAttr, CatAttr
from bokeh.models import HoverTool
from bokeh.layouts import gridplot
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
rootPath = '/Users/apple/desktop/intern/HPE/'
#rootPath = 'C:/Users/yuehw/Desktop/Samsung_PM1633a_480GB_VEMLC_WCE_HP01_Win_PS_Results/'
fileList = ['PS_v5_1920_Seq_Results.xml','PS_v5_960_Seq_Results.xml','PS_v5_480_Seq_Results.xml','PS_v5_240_Seq_Results.xml']
P_240,P_480,P_960,P_1920 = [],[],[],[]
rawArray = [P_240,P_480,P_960,P_1920]
rawFeature = ['queue-depth','read-pct','block-size','iops','mbps','rt','max-rt']
numberOfAttrib = 1
queue = 1
read_pct = 2
block_size = 3
iops = 4
aveLatency = 6
maxLatency = 7

def saveRawData_attrib(parent,rawData,idx):
    rawArray[idx].append(float(parent.get(rawData)))

def saveRawData_float(parent,rawData,idx):
    for i in parent.iter(rawData):            
        rawArray[idx].append(float(i.text))
        break
def countMiB(MiB):
    row = len(rawArray[0])
    fileLength = len(fileList) 
    for i in range(0,row):
        for idx in range(0,fileLength):     
            MiB[idx + i*fileLength] = rawArray[idx][i,block_size]*rawArray[idx][i,iops]/2**20

def groups(group):
    row = len(rawArray[0])
    fileLength = len(fileList)
    for i in range(0,row): 
        tmpString = byte(rawArray[0][i,block_size]) + '@Q' + str(int(rawArray[0][i,queue]))
        for idx in range(0,fileLength):
            group.append(tmpString)
            
def byte(blk):
    if blk < 2**10:
        return str(int(blk)) + ''
    elif blk >= 2**20:
        return str(int(blk/2**20)) + 'M'
    else: 
        return str(int(blk/2**10)) + 'K'

def aggres(aggre):
    devices = ['1920GB','960GB','480GB','240GB']         # not generalized
    row = len(rawArray[0])
    devLength = len(devices)
    for i in range(0,row): 
        for idx in range(0,devLength):
            aggre.append(devices[idx])

def plotG(data, ttl):
    fig = Bar(data, label=CatAttr(columns=['Group'], sort=False), values='Height', group='Spec', legend=True
        ,plot_width=1000, plot_height=600, title=ttl, ylabel = 'MiB/s')
    fig.title.text_font_size = '18pt'
    # Show value in img
    fig.add_tools(HoverTool())
    hover = fig.select(dict(type=HoverTool))
    hover.tooltips = [('Spec',' $x'),('MiB/s',' @height')]
    return fig

for idx in range(0,len(fileList)):
    tree = ET.parse(fileList[idx])
    root = tree.getroot()
    
    for phase in root.iter('phase'):
        saveRawData_attrib(phase,'number',idx)
        for i in range(0, len(rawFeature)):
            saveRawData_float(phase,rawFeature[i],idx)
    rawArray[idx] = np.reshape(np.asarray(rawArray[idx]),(-1,len(rawFeature) + numberOfAttrib))
    
MiB = np.zeros((len(rawArray[idx])*len(rawArray))) 
group, aggre = [],[]  
countMiB(MiB)
groups(group)
aggres(aggre)
fig = plotG(pd.DataFrame({'Group':group[0:224], 'Spec':aggre[0:224], 'Height':MiB[0:224]}),"Sequential Read Performance")
fig2 = plotG(pd.DataFrame({'Group':group[224:], 'Spec':aggre[224:], 'Height':MiB[224:]}),"Sequential Write Performance")

output_file('chartsBarTest.html')
show(gridplot([[fig],[fig2]]))



