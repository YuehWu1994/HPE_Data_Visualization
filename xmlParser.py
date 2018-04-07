import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
    
    
        
            
def plotMib(MiB):
    WR_pivot = int(len(rawArray[0])/2)
    ind = np.arange(WR_pivot)  # the x locations for the groups
    width = 0.2                           # the width of the bars
    fig = plt.figure(figsize=(25,15))
    ax = fig.add_subplot(211)
    rects0 = ax.bar(ind, MiB[:WR_pivot,0], width, color='r')
    rects1 = ax.bar(ind + width, MiB[:WR_pivot,1], width, color='y')
    rects2 = ax.bar(ind + width*2, MiB[:WR_pivot,2], width, color='b')
    rects3 = ax.bar(ind + width*3, MiB[:WR_pivot,3], width, color='g')
    ax.legend((rects0[0], rects1[0],rects2[0], rects3[0]), ('1920G','960G','480G','240G'))
    
    
    plt.ylabel('MiB/s',fontsize=20,fontweight='bold')
    plt.title('Sequential Read Performance',fontsize=20,fontweight='bold')
    plt.xticks(ind + width / 2, ('A', 'B', 'C', 'D', 'E'))
    
    ax = fig.add_subplot(212)
    rects0 = ax.bar(ind, MiB[WR_pivot:,0], width, color='r')
    rects1 = ax.bar(ind + width, MiB[WR_pivot:,1], width, color='y')
    rects2 = ax.bar(ind + width*2, MiB[WR_pivot:,2], width, color='b')
    rects3 = ax.bar(ind + width*3, MiB[WR_pivot:,3], width, color='g')
    ax.legend((rects0[0], rects1[0],rects2[0], rects3[0]), ('1920G','960G','480G','240G'))
    
    
    plt.ylabel('MiB/s',fontsize=20,fontweight='bold')
    plt.title('Sequential Write Performance',fontsize=20,fontweight='bold')
    plt.xticks(ind + width / 2, ('A', 'B', 'C', 'D', 'E'))  
    plt.show()

def plotLatency():
    
    WR_pivot = int(len(rawArray[0])/2)
    ind = np.arange(WR_pivot)
    plt.figure(figsize=(10,20))
    # Ave_W&R
    blue_patch = mpatches.Patch(color='blue', label='1920G')
    yellow_patch = mpatches.Patch(color='yellow', label='960G')
    red_patch = mpatches.Patch(color='red', label='480G')
    green_patch = mpatches.Patch(color='green', label='240G')
    
    plt.subplot(411)
    plt.plot(ind,rawArray[0][:WR_pivot,aveLatency],'bo',ind,rawArray[0][:WR_pivot,aveLatency],'k')
    plt.plot(ind,rawArray[1][:WR_pivot,aveLatency],'yo',ind,rawArray[1][:WR_pivot,aveLatency],'k')
    plt.plot(ind,rawArray[2][:WR_pivot,aveLatency],'ro',ind,rawArray[2][:WR_pivot,aveLatency],'k')
    plt.plot(ind,rawArray[3][:WR_pivot,aveLatency],'go',ind,rawArray[3][:WR_pivot,aveLatency],'k')
    plt.legend(handles=[blue_patch,yellow_patch,red_patch,green_patch],bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    plt.ylabel('mSec',fontsize=20,fontweight='bold')
    plt.title('Sequential Read Average Latency',fontsize=20,fontweight='bold')
    
    plt.subplot(412)
    plt.plot(ind,rawArray[0][WR_pivot:,aveLatency],'bo',ind,rawArray[0][WR_pivot:,aveLatency],'k')
    plt.plot(ind,rawArray[1][WR_pivot:,aveLatency],'yo',ind,rawArray[1][WR_pivot:,aveLatency],'k')
    plt.plot(ind,rawArray[2][WR_pivot:,aveLatency],'ro',ind,rawArray[2][WR_pivot:,aveLatency],'k')
    plt.plot(ind,rawArray[3][WR_pivot:,aveLatency],'go',ind,rawArray[3][WR_pivot:,aveLatency],'k')
    plt.legend(handles=[blue_patch,yellow_patch,red_patch,green_patch],bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    plt.ylabel('mSec',fontsize=20,fontweight='bold')
    plt.title('Sequential Write Average Latency',fontsize=20,fontweight='bold')
    
    plt.subplot(413)
    plt.plot(ind,rawArray[0][:WR_pivot,maxLatency],'bo',ind,rawArray[0][:WR_pivot,maxLatency],'k')
    plt.plot(ind,rawArray[1][:WR_pivot,maxLatency],'yo',ind,rawArray[1][:WR_pivot,maxLatency],'k')
    plt.plot(ind,rawArray[2][:WR_pivot,maxLatency],'ro',ind,rawArray[2][:WR_pivot,maxLatency],'k')
    plt.plot(ind,rawArray[3][:WR_pivot,maxLatency],'go',ind,rawArray[3][:WR_pivot,maxLatency],'k')
    plt.legend(handles=[blue_patch,yellow_patch,red_patch,green_patch],bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    plt.ylabel('mSec',fontsize=20,fontweight='bold')
    plt.title('Sequential Read Max Latency',fontsize=20,fontweight='bold')
    
    plt.subplot(414)
    plt.plot(ind,rawArray[0][WR_pivot:,maxLatency],'bo',ind,rawArray[0][WR_pivot:,maxLatency],'k')
    plt.plot(ind,rawArray[1][WR_pivot:,maxLatency],'yo',ind,rawArray[1][WR_pivot:,maxLatency],'k')
    plt.plot(ind,rawArray[2][WR_pivot:,maxLatency],'ro',ind,rawArray[2][WR_pivot:,maxLatency],'k')
    plt.plot(ind,rawArray[3][WR_pivot:,maxLatency],'go',ind,rawArray[3][WR_pivot:,maxLatency],'k')
    plt.legend(handles=[blue_patch,yellow_patch,red_patch,green_patch],bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    plt.ylabel('mSec',fontsize=20,fontweight='bold')
    plt.title('Sequential Write Max Latency',fontsize=20,fontweight='bold')
    
    plt.show()


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
#plotMib(MiB)
plotLatency()






