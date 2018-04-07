import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
rootPath = '/Users/apple/desktop/intern/HPE/'
#rootPath = 'C:/Users/yuehw/Desktop/Samsung_PM1633a_480GB_VEMLC_WCE_HP01_Win_PS_Results/'
fileList = ['PS_v5a_3840_Rand_Results.xml','PS_v5a_1920_Rand_Results.xml','PS_v5a_960_Rand_Results.xml','PS_v5a_480_Rand_Results.xml']
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

mixTag = False
mixPhase = 0

def queueModify(parent):
    count = 0
    for target in parent.iter('target-device'):
        count += 1
    return count
    
def saveRawData_attrib(parent,rawData,idx):
    rawArray[idx].append(float(parent.get(rawData)))

def saveRawData_float(parent,rawData,idx):
    for i in parent.iter(rawData):            
        temp = float(i.text)
        # special case        
        if rawData == 'queue-depth':
            temp *= queueModify(parent)
        if rawData == 'read-pct' and temp != 100 and temp != 0 and mixTag == False:
            global mixTag 
            global mixPhase
            mixPhase = int(rawArray[idx][len(rawArray[idx]) - read_pct] - 1) 
            mixTag = True
    rawArray[idx].append(temp) 
    
def countMiB(MiB):
    row = mixPhase
    fileLength = len(fileList) 
    for i in range(0,row):
        for idx in range(0,fileLength):        
            MiB[idx + i*fileLength] = rawArray[idx][i,iops]

def groups(group):
    row = mixPhase
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
    row = mixPhase
    devLength = len(devices)
    for i in range(0,row): 
        for idx in range(0,devLength):
            aggre.append(devices[idx])

def plotMib():
    WR_pivot = int(mixPhase/2)                         # how the last 3 phase come?
    ind = np.arange(WR_pivot)             # the x locations for the groups
    width = 0.2                           # the width of the bars
    fig = plt.figure(figsize=(25,15))
    ax = fig.add_subplot(211)
    rects0 = ax.bar(ind,           rawArray[0][:WR_pivot,iops], width, color='r')
    rects1 = ax.bar(ind + width,   rawArray[1][:WR_pivot,iops], width, color='y')
    rects2 = ax.bar(ind + width*2, rawArray[2][:WR_pivot,iops], width, color='b')
    rects3 = ax.bar(ind + width*3, rawArray[3][:WR_pivot,iops], width, color='g')
    ax.legend((rects0[0], rects1[0],rects2[0], rects3[0]), ('3840G','1920G','960G','480G'))
       
    plt.ylabel('MiB/s',fontsize=20,fontweight='bold')
    plt.title('Sequential Write Performance',fontsize=20,fontweight='bold')
    plt.xticks(ind + width / 2, ('A', 'B', 'C', 'D', 'E'))
    
    ax = fig.add_subplot(212)
    rects0 = ax.bar(ind,           rawArray[0][WR_pivot:mixPhase,iops], width, color='r')
    rects1 = ax.bar(ind + width,   rawArray[1][WR_pivot:mixPhase,iops], width, color='y')
    rects2 = ax.bar(ind + width*2, rawArray[2][WR_pivot:mixPhase,iops], width, color='b')
    rects3 = ax.bar(ind + width*3, rawArray[3][WR_pivot:mixPhase,iops], width, color='g')
    ax.legend((rects0[0], rects1[0],rects2[0], rects3[0]), ('3840G','1920G','960G','480G'))
       
    plt.ylabel('MiB/s',fontsize=20,fontweight='bold')
    plt.title('Sequential Read Performance',fontsize=20,fontweight='bold')
    plt.xticks(ind + width / 2, ('A', 'B', 'C', 'D', 'E'))  
    plt.show()

def plotLatency():
    WR_pivot = int(mixPhase/2) 
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
    plt.plot(ind,rawArray[0][WR_pivot:mixPhase,aveLatency],'bo',ind,rawArray[0][WR_pivot:mixPhase,aveLatency],'k')
    plt.plot(ind,rawArray[1][WR_pivot:mixPhase,aveLatency],'yo',ind,rawArray[1][WR_pivot:mixPhase,aveLatency],'k')
    plt.plot(ind,rawArray[2][WR_pivot:mixPhase,aveLatency],'ro',ind,rawArray[2][WR_pivot:mixPhase,aveLatency],'k')
    plt.plot(ind,rawArray[3][WR_pivot:mixPhase,aveLatency],'go',ind,rawArray[3][WR_pivot:mixPhase,aveLatency],'k')
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
    plt.plot(ind,rawArray[0][WR_pivot:mixPhase,maxLatency],'bo',ind,rawArray[0][WR_pivot:mixPhase,maxLatency],'k')
    plt.plot(ind,rawArray[1][WR_pivot:mixPhase,maxLatency],'yo',ind,rawArray[1][WR_pivot:mixPhase,maxLatency],'k')
    plt.plot(ind,rawArray[2][WR_pivot:mixPhase,maxLatency],'ro',ind,rawArray[2][WR_pivot:mixPhase,maxLatency],'k')
    plt.plot(ind,rawArray[3][WR_pivot:mixPhase,maxLatency],'go',ind,rawArray[3][WR_pivot:mixPhase,maxLatency],'k')
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
MiB = np.zeros(mixPhase * len(rawArray)) 

group, aggre = [],[]  
countMiB(MiB)
groups(group)
aggres(aggre)
    
#plotMib()
#plotLatency()
