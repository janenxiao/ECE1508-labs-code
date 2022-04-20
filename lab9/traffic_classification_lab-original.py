# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 10:38:33 2019

@author: synchromedia
"""

#from pandas.tools.plotting import scatter_matrix
import time
import pandas
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.preprocessing import StandardScaler


##################################################################################
# **************** Functions for the classification file 1  **********************
##################################################################################
# In the following lines, you will find the functions that has been used to 
#calculate the features of each flow and stored in the feature matrix.
def check_src_port_values(r):
    c1 = r.split(' ')    
    if(c1[2]=='>'):
        return c1[0]
        
def check_dst_port_values(r):
    c1 = r.split(' ')
    if(c1[2]=='>'):
        return c1[4]    


def sort_mydata(ips):
    
    if(len(ips)<4):
        return 'ERROR_IN_DATA'
    if (ips[0] < ips[1]): 
        new_ips1 = ips[0]+'>'+ips[1] + '>'
        
    else:
        new_ips1 = ips[1]+'>'+ips[0]+'>'
    a=ips[2]
    b=ips[3]
    c=''.join(str(ord(c)) for c in a)
    d=''.join(str(ord(c)) for c in b)
    
    if (c < d): 
        new_ips2 = a+'>'+b
       
    else:
        new_ips2 = b+'>'+a

    new_ips=new_ips1+new_ips2
    return new_ips

def check_retransmitted(mst):
    nbr=0
    for m in mst:
       
        if('Retransmission]' in m):
            nbr += 1
        else: nbr=nbr
    return nbr

def check_ack(lst):
    val=0
    for l in lst:
        if('ACK' in l):
            val += 1
        else: val=val
    return val

def check_push(lst):
    s=0
    for l in lst:
        if('PSH' in l):
            s +=1
        else: s=s
    return s

def check_Syn(lst):
    m=0
    for l in lst:
        if('SYN' in l):
            m +=1
        else : m=m
    return m

def check_Urg(lst):
    j=0
    for l in lst:
        if('URG' in l):
            j +=1
        else : j=j
    return j

def check_rack(lst):
    j=0
    for l in lst:
        if('TCP duplicate ACK dup' in l):
            j +=1
        else : j=j
    return j

def check_mss(lst):
    for l in lst:
        if('MSS' in l):
            return l
        
        
def check_number4(list_check):
    r=0
    s = str(list_check)
    if(s!='0'):
        p=s.split('=')
        if(len(p)>1):
            r=int(p[1])
    return r

def check_SACK(lst):
    g=0
    for l in lst:
        if('SACK' in l):
            g +=1
        else : g=g
    return g

def check_RST(lst):
    d=0
    for l in lst:
        if('RST' in l):
            d +=1
        else :d=d
    return d  

def check_FIN(lst):
    d=0
    for l in lst:
        if('FIN' in l):
            d +=1
        else: d=d
    return d

##################################################################################
# **************** Functions for the classification file 2  **********************
################################################################################## 
# In the following lines, you will find the functions that has been used to 
#calculate the features of each flow and stored in the feature matrix.
    ##### Sinece the structure of the second file is different than the first 
    ##### file, some functions may have changed, others not.

def check_src_port_values3(r):
    c1 = r.split(' ')
    
    if(c1[0]=='[TCP'):
        c2= r.split('>')
        c3=c2[0].split(' ')
        c3 = [e for e in c3 if e!='']
        return c3[-1]
    else :
        c2 = [e for e in c1 if e!='']
        return c2[0]
   

def check_dst_port_values3(r):
    c1 = r.split(' ')
    if(c1[0]=='[TCP'):
        c2= r.split('>')
        c3=c2[1].split(' ')
        c3 = [e for e in c3 if e!='']
        return c3[0]
    else:
        c2=r.split('>')
        c3=c2[1].split(' ')
        c3 = [e for e in c3 if e!='']
        return c3[0]
        


def func1(inf):
    if(inf[0:7]=='[Packet'):
        return False
    return True

def check_retransmitted2(mst):
    nbr=0
    for m in mst:
       
        if('Retransmission]' in m):
            nbr += 1
        else: nbr=nbr
    return nbr

def check_ack2(lst):
    val=0
    for l in lst:
        if('ACK' in l):
            val += 1
        else: val=val
    return val

def check_rack2(lst):
    j=0
    for l in lst:
        if('TCP duplicate ACK dup' in l):
            j +=1
        else: j=j
    return j

def check_push2(lst):
    s=0
    for l in lst:
        if('PSH' in l):
            s +=1
        else: s=s
    return s

def check_Syn2(lst):
    m=0
    for l in lst:
        if('SYN' in l):
            m +=1
        else: m=m
    return m

def check_Urg2(lst):
    j=0
    for l in lst:
        if('URG' in l):
            j +=1
        else: j=j
    return j

def check_mss2(lst):
    for l in lst:
        if('MSS' in l):
            return l
        
        
def check_number42(list_check):
    r=0
    s = str(list_check)
    if(s!='0'):
        p=s.split('=')
        if(len(p)>1):
            r=int(p[1])
    return r

def check_SACK2(lst):
    g=0
    for l in lst:
        if('SACK' in l):
            g +=1
        else: g=0
    return g

def check_RST2(lst):
    d=0
    for l in lst:
        if('RST' in l):
            d +=1
        else: d=0
    return d

def check_FIN2(lst):
    d=0
    for l in lst:
        if('FIN' in l):
            d +=1
        else: d=0
    return d    
##################################################################################
# ******************************* The ground truth *******************************
##################################################################################


app_list = {'Mail':1, 'bittorrent.exe':3, 'firefox-bin':0, 'Skype':2, 'thunderbird-bin':1,
            'firefox':0, 'PubSubAgent':0, 'Safari':0, 'DashboardClient':0, 'privoxy':0,
            'iTunes':0, 'gnome-panel':0, 'SVCHOST.EXE':1, 'Safari Webpage P':0,
            'adeona-client.ex':0, 'iCal':0, 'ssh':5, 'Transmission':0, 'vmnet-natd':0,
            'OctoshapeClient.exe':0, 'firefox.exe':0, 'skype':2, 'Synergy':0,
            'dashboardadvisor':0, 'Microsoft Ship A':0, 'GoogleSoftwareUp':1, 'amule':4,
            'ocspd':0, 'opera':1, 'Skype.exe':2, 'SubmitReport':1, 'Microsoft AU Dae':0,
            'Microsoft AutoUp':0, 'btdna.exe':0, 'svchost.exe':0, 'thunderbird.exe':0,
            'Skype$$$$hdiutil$$$$bash$$$$cp':2, 'ntpd':2, 'kdeinit4':0,
            'Microsoft Error':0, 'Safari Webpage':0, 'msmsgs.exe':5, 'ashWebSv.exe':0,
            'avast.setup':0, 'Microsoft Messen':1, 'SubmitDiagInfo':1, 'iCyclone':0,
            'iStat menus Back':0, 'vmware':0, 'Software Update':0, 'svn':1,
            'GoogleSoftwareU':1, 'TeXShop':0, 'LUCOMS~1.EXE':0, 'Cyberduck':0,
            'Adobe Updater':0, 'seamonkey.exe':0, 'Aquamacs Emacs':0, 'SuperDuper!':0,
            'Dictionary':0, 'Skim':0, 'Calculator':0, 'GrowlHelperApp':0,
            'SoftwareUpdateCh':0, 'freshclam':0, 'skypePM.exe':2, 'javaw.exe':0,
            'Parallels':0, 'PDF Shrink':0, 'whois':5}

#C:/Users/synchromedia/Desktop/python projet/
# Here we read the ground truth csv file and we reorganize into a new datframe called nvgt

gt = pandas.read_csv("gt.csv")
gt2 = gt[gt.columns[0]].values.tolist()
gt3 = [s.split(':') for s in gt2]
nvgt = pandas.DataFrame(gt3)

nvgt.columns = ['TimeStamp','IP src','IP dst','Port src','Port dst','DPI','App','Protocol']

# We create the column 'mydata_MERGED' that will characterize each flow by it source and destination IP adresses, source and 
#destination port numbers and protocol.

nvgt['mydata_MERGED'] = (nvgt['IP src'] + '>' + nvgt['IP dst'] + '>'+ nvgt['Port src'] + '>'+nvgt['Port dst']+'>'+ nvgt['Protocol']).map(lambda x: sort_mydata(x.split('>')))

nvgt.sort_values(by=['TimeStamp'], inplace=True)#par temps ou bien par mydata_me

#We create the column label that will hold the name of each application representing the class of flows
nvgt['Label'] = nvgt['App'].apply(lambda app: app_list[app])


##################################################################################
# *************************** Classification file 1  *****************************
##################################################################################

# Read the csv file containing the traffic traces and store it in a dataframe called mydata2
mydata2 = pandas.read_csv('file2_2')

# Extract port number from the Info filed
mydata2['Port_src'] = mydata2['Info'].map(lambda r: check_src_port_values(r))
mydata2['Port_dst'] = mydata2['Info'].map(lambda r: check_dst_port_values(r))

# We create the column 'mydata_MERGED' that will characterize each flow by it source and destination IP adresses, source and 
#destination port numbers and protocol.
mydata2['mydata_MERGED'] = (mydata2['Source'] + '>' + mydata2['Destination'] + '>'+ mydata2['Port_src'] + '>'+mydata2['Port_dst']+'>'+ mydata2['Protocol']).map(lambda x: sort_mydata(str(x).split('>')))
mydata2 = mydata2[mydata2['mydata_MERGED']!='ERROR_IN_DATA'].copy(deep=True)


# Now we will select the number of packets in each flow : this aims at providing an online classification as opposed to offline classification, 
#where we have to wait for all packets to be received in order to start the classification
# Your task will be to change this number and compare the classificaton performances between different algorithms.
number_of_packet_in_flow = 50
mydata2.sort_values(by=['Time'], inplace=True)#par temps ou bien par mydata_me
mydata2['Packet_Order'] = mydata2.groupby(['mydata_MERGED'])['No.'].cumcount()
mydata_selected = mydata2[mydata2['Packet_Order']<number_of_packet_in_flow].copy(deep=True)

# The new dataframe that includes only number_of_packet_in_flow is called mydata_selected and now we will start calculating the features
# to build the feature matrix.  It is worth mentionning that the features here are calcultaed through the function above.

# Feature : Inter arrival time which the time between the time two packets arrive to the network
mydata_selected.sort_values(by=['Time'], inplace=True)
mydata_selected['Packet_Inter_Arrival_Time'] = mydata_selected.groupby(['mydata_MERGED'])['Time'].diff().fillna(0)
Inter_Arriv_Mean = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].mean().reset_index()
Inter_Arriv_Var = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].var().reset_index().fillna(0)
Inter_Arriv_STD = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].std().reset_index().fillna(0)
Inter_Arriv_MIN = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].min().reset_index()
Inter_Arriv_MAX = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].max().reset_index()


# Feature : The number of retransmissions 
mydata_selected['Retrans_Count'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_retransmitted(x.split()))

# Feature : The number of acknowlegments
mydata_selected['Nbr_ACK'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_ack(x.split()))

# Feature : The number of packets pushed to transmission     
mydata_selected['Nbr_PSH'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_push(x.split()))

# Feature : The number of synchronization packets
mydata_selected['Nbr_SYN'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_Syn(x.split()))

# Feature : The number of ugent flags    
mydata_selected['Nbr_Urg'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_Urg(x.split()))


# Feature : The number of Racks
mydata_selected['Nbr_RACK'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_rack(x.split()))

# Feature : MSS characteristics
    
mydata_selected['MSS_chk'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_mss(x.split())).fillna(0)
mydata_selected['MSS_Value'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['MSS_chk'].map(lambda x: check_number4(x)).fillna(0)
MSS_Mean = mydata_selected.groupby(['mydata_MERGED'])['MSS_Value'].mean().reset_index()
MSS_Var = mydata_selected.groupby(['mydata_MERGED'])['MSS_Value'].var().reset_index().fillna(0)
MSS_STD = mydata_selected.groupby(['mydata_MERGED'])['MSS_Value'].std().reset_index().fillna(0)
MSS_MIN = mydata_selected.groupby(['mydata_MERGED'])['MSS_Value'].min().reset_index()
MSS_MAX = mydata_selected.groupby(['mydata_MERGED'])['MSS_Value'].max().reset_index()

# Feature : Packet length

Len_Mean = mydata_selected.groupby(['mydata_MERGED'])['Length'].mean().reset_index()
Len_Var = mydata_selected.groupby(['mydata_MERGED'])['Length'].var().reset_index().fillna(0)
Len_STD = mydata_selected.groupby(['mydata_MERGED'])['Length'].std().reset_index().fillna(0)
Len_MIN = mydata_selected.groupby(['mydata_MERGED'])['Length'].min().reset_index()
Len_MAX = mydata_selected.groupby(['mydata_MERGED'])['Length'].max().reset_index()

# Feature : Inter packet length
mydata_selected['Packet_Inter_Len'] = mydata_selected.groupby(['mydata_MERGED'])['Length'].diff().fillna(0)
mydata_selected['Packet_Inter_Len']=abs(mydata_selected['Packet_Inter_Len'])
Inter_Len_Mean = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Len'].mean().reset_index()
Inter_Len_Var = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Len'].var().reset_index().fillna(0)
Inter_Len_STD = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Len'].std().reset_index().fillna(0)
Inter_Len_MIN = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Len'].min().reset_index()
Inter_Len_MAX = mydata_selected.groupby(['mydata_MERGED'])['Packet_Inter_Len'].max().reset_index()

# Feature : SACK number
#SACK number: SACKs allow a receiver to acknowledge non-consecutive data, 
#so that the sender can retransmit only what is missing at the receivers end. 

mydata_selected['Nbr_SACK'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_SACK(x.split()))

# Feature : Number of reset 
mydata_selected['Nbr_RST'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_RST(x.split()))

# Feature : Number of Fin packet
#Fin packet counts the number of session terminated  
mydata_selected['Nbr_FIN'] = mydata_selected.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_FIN(x.split()))

# Now that we have calculated all the features, we organize them in a new matrix called MY_FEATURE_TABLE: this is our feature matrix 
#and its columns include the name of the flow (reporesented by the column 'mydata_MERGED') and all the features we calculated.


columns=['Retrans_Count','Nbr_ACK','Nbr_PSH','Nbr_SYN','Nbr_Urg', 'Nbr_SACK', 'Nbr_RST', 'Nbr_FIN','Nbr_RACK']

MY_FEATURE_TABLE = mydata_selected.groupby('mydata_MERGED')[columns].sum().reset_index()

Inter_Arriv_Mean.columns = ['mydata_MERGED', 'Inter_Arriv_Mean']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Arriv_Mean, on='mydata_MERGED', how='left')
Inter_Arriv_Var.columns = ['mydata_MERGED', 'Inter_Arriv_Var']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Arriv_Var, on='mydata_MERGED', how='left')
Inter_Arriv_STD.columns = ['mydata_MERGED', 'Inter_Arriv_STD']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Arriv_STD, on='mydata_MERGED', how='left')
Inter_Arriv_MIN.columns = ['mydata_MERGED', 'Inter_Arriv_MIN']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Arriv_MIN, on='mydata_MERGED', how='left')
Inter_Arriv_MAX.columns = ['mydata_MERGED', 'Inter_Arriv_MAX']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Arriv_MAX, on='mydata_MERGED', how='left')

Len_Mean.columns = ['mydata_MERGED', 'Len_Mean']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Len_Mean, on='mydata_MERGED', how='left')
Len_Var.columns = ['mydata_MERGED', 'Len_Var']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Len_Var, on='mydata_MERGED', how='left')
Len_MIN.columns = ['mydata_MERGED', 'Len_MIN']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Len_MIN, on='mydata_MERGED', how='left')
Len_MAX.columns = ['mydata_MERGED', 'Len_MAX']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Len_MAX, on='mydata_MERGED', how='left')

Inter_Len_Mean.columns = ['mydata_MERGED', 'Inter_Len_Mean']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Len_Mean, on='mydata_MERGED', how='left')
Inter_Len_Var.columns = ['mydata_MERGED', 'Inter_Len_Var']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Len_Var, on='mydata_MERGED', how='left')
Inter_Len_STD.columns = ['mydata_MERGED', 'Inter_Len_STD']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Len_STD, on='mydata_MERGED', how='left')
Inter_Len_MIN.columns = ['mydata_MERGED', 'Inter_Len_MIN']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Len_MIN, on='mydata_MERGED', how='left')
Inter_Len_MAX.columns = ['mydata_MERGED', 'Inter_Len_MAX']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, Inter_Len_MAX, on='mydata_MERGED', how='left')

MSS_Mean.columns = ['mydata_MERGED', 'MSS_Mean']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, MSS_Mean, on='mydata_MERGED', how='left')
MSS_Var.columns = ['mydata_MERGED', 'MSS_Var']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, MSS_Var, on='mydata_MERGED', how='left')
MSS_STD.columns = ['mydata_MERGED', 'MSS_STD']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, MSS_STD, on='mydata_MERGED', how='left')
MSS_MIN.columns = ['mydata_MERGED', 'MSS_MIN']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, MSS_MIN, on='mydata_MERGED', how='left')
MSS_MAX.columns = ['mydata_MERGED', 'MSS_MAX']
MY_FEATURE_TABLE = pandas.merge(MY_FEATURE_TABLE, MSS_MAX, on='mydata_MERGED', how='left')


#The next step consists on merging the feature table with ground truth in order to add a new columns called label.
# Through this column, each flow will have its own label and this will be used in the model training phase.

tmp = nvgt[['mydata_MERGED', 'Label']]
merged_inner = pandas.merge(MY_FEATURE_TABLE, tmp, on='mydata_MERGED', how='left')
dataset2 = merged_inner[merged_inner.columns[1:]].copy(deep=True)
dataset2 = dataset2[-dataset2['Label'].isnull()].copy(deep=True)

#The final result (feature matrix) is stored in dataset2.

##################################################################################
# *************************** Classification file 2  *****************************
##################################################################################

#We will do the same steps as for the first file: the aim of this is to have more samples for the classification.



# Read the csv file containing the traffic traces and store it in a dataframe called mydata2
#mydatatest = pandas.read_csv('file3_3')
mydatatest = pandas.read_csv('file3_3', engine = 'python',  error_bad_lines=False)

# Delete some unwanted packets.
mydatatest['tmp_clm'] = mydatatest['Info'].map(lambda i: func1(i))
mydatac = mydatatest[mydatatest['tmp_clm']==True]
mydata3=mydatac.copy(deep=True)

# Extract port number from the Info filed
mydata3['Port_src'] = mydata3['Info'].map(lambda r: check_src_port_values3(r))
mydata3['Port_dst'] = mydata3['Info'].map(lambda r: check_dst_port_values3(r))

# We create the column 'mydata_MERGED' that will characterize each flow by it source and destination IP adresses, source and 
#destination port numbers and protocol.
mydata3['mydata_MERGED'] = (mydata3['Source'] + '>' + mydata3['Destination'] + '>'+ mydata3['Port_src'] + '>'+mydata3['Port_dst']+'>'+ mydata3['Protocol']).map(lambda x: sort_mydata(str(x).split('>')))
mydata3 = mydata3[mydata3['mydata_MERGED']!='ERROR_IN_DATA'].copy(deep=True)

# Now we will select the number of packets in each flow : this aims at providing an online classification as opposed to offline classification, 
#where we have to wait for all packets to be received in order to start the classification
# Your task will be to change this number and compare the classificaton performances between different algorithms.
mydata3.sort_values(by=['Time'], inplace=True)
mydata3['Packet_Order'] = mydata3.groupby(['mydata_MERGED'])['No.'].cumcount()
mydata_selected3 = mydata3[mydata3['Packet_Order']<number_of_packet_in_flow].copy(deep=True)


# The new dataframe that includes only number_of_packet_in_flow is called mydata_selected3 and now we will start calculating the features
# to build the feature matrix.  It is worth mentionning that the features here are calcultaed through the function above.
mydata_selected3.sort_values(by=['Time'], inplace=True)

# Feature : Inter arrival time which the time between the time two packets arrive to the network
mydata_selected3['Packet_Inter_Arrival_Time'] = mydata_selected3.groupby(['mydata_MERGED'])['Time'].diff().fillna(0) 
Inter_Arriv_Mean3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].mean().reset_index()
Inter_Arriv_Var3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].var().reset_index().fillna(0)
Inter_Arriv_STD3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].std().reset_index().fillna(0)
Inter_Arriv_MIN3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].min().reset_index()
Inter_Arriv_MAX3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Arrival_Time'].max().reset_index()

# Feature : The number of retransmissions 
mydata_selected3['Retrans_Count'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_retransmitted2(x.split()))

# Feature : The number of acknowlegments
mydata_selected3['Nbr_ACK'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_ack2(x.split()))

# Feature : The number of Racks    
mydata_selected3['Nbr_RACK'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_rack2(x.split()))

# Feature : The number of packets pushed to transmission     
mydata_selected3['Nbr_PSH'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_push2(x.split()))

# Feature : The number of synchronization packets
mydata_selected3['Nbr_SYN'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_Syn2(x.split()))

# Feature : The number of ugent flags      
mydata_selected3['Nbr_Urg'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_Urg2(x.split()))

# Feature : MSS characteristics
mydata_selected3['MSS_chk'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_mss2(x.split())).fillna(0)
mydata_selected3['MSS_Value'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['MSS_chk'].map(lambda x: check_number42(x)).fillna(0)
MSS_Mean3 = mydata_selected3.groupby(['mydata_MERGED'])['MSS_Value'].mean().reset_index()
MSS_Var3 = mydata_selected3.groupby(['mydata_MERGED'])['MSS_Value'].var().reset_index().fillna(0)
MSS_STD3 = mydata_selected3.groupby(['mydata_MERGED'])['MSS_Value'].std().reset_index().fillna(0)
MSS_MIN3 = mydata_selected3.groupby(['mydata_MERGED'])['MSS_Value'].min().reset_index()
MSS_MAX3 = mydata_selected3.groupby(['mydata_MERGED'])['MSS_Value'].max().reset_index()

# Feature : Packet length
Len_Mean3 = mydata_selected3.groupby(['mydata_MERGED'])['Length'].mean().reset_index()
Len_Var3 = mydata_selected3.groupby(['mydata_MERGED'])['Length'].var().reset_index().fillna(0)
Len_STD3 = mydata_selected3.groupby(['mydata_MERGED'])['Length'].std().reset_index().fillna(0)
Len_MIN3 = mydata_selected3.groupby(['mydata_MERGED'])['Length'].min().reset_index()
Len_MAX3 = mydata_selected3.groupby(['mydata_MERGED'])['Length'].max().reset_index()

# Feature : Inter packet length
mydata_selected3['Packet_Inter_Len'] = mydata_selected3.groupby(['mydata_MERGED'])['Length'].diff().fillna(0)
mydata_selected3['Packet_Inter_Len']=abs(mydata_selected3['Packet_Inter_Len'])
Inter_Len_Mean3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Len'].mean().reset_index()
Inter_Len_Var3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Len'].var().reset_index().fillna(0)
Inter_Len_STD3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Len'].std().reset_index().fillna(0)
Inter_Len_MIN3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Len'].min().reset_index()
Inter_Len_MAX3 = mydata_selected3.groupby(['mydata_MERGED'])['Packet_Inter_Len'].max().reset_index()

#SACK number: SACKs allow a receiver to acknowledge non-consecutive data, 
#so that the sender can retransmit only what is missing at the receivers end.    
mydata_selected3['Nbr_SACK'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_SACK2(x.split()))
#
# Feature : The number of retransmissions 
mydata_selected3['Nbr_RST'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_RST2(x.split()))

# Feature : Number of Fin packet
#Fin packet counts the number of session terminated   
mydata_selected3['Nbr_FIN'] = mydata_selected3.sort_values(by=['mydata_MERGED','Time'], inplace=False)['Info'].map(lambda x: check_FIN2(x.split()))


# Now that we have calculated all the features, we organize them in a new matrix called MY_FEATURE_TABLE3: this is our feature matrix 
#and its columns include the name of the flow (represented by the column 'mydata_MERGED') and all the features we calculated.
columns=['Retrans_Count','Nbr_ACK','Nbr_PSH','Nbr_SYN','Nbr_Urg', 'Nbr_SACK', 'Nbr_RST', 'Nbr_FIN','Nbr_RACK']

MY_FEATURE_TABLE3 = mydata_selected3.groupby('mydata_MERGED')[columns].sum().reset_index()

Inter_Arriv_Mean3.columns = ['mydata_MERGED', 'Inter_Arriv_Mean']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Arriv_Mean3, on='mydata_MERGED', how='left')

Inter_Arriv_Var3.columns = ['mydata_MERGED', 'Inter_Arriv_Var']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Arriv_Var3, on='mydata_MERGED', how='left')

Inter_Arriv_STD3.columns = ['mydata_MERGED', 'Inter_Arriv_STD']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Arriv_STD3, on='mydata_MERGED', how='left')

Inter_Arriv_MIN3.columns = ['mydata_MERGED', 'Inter_Arriv_MIN']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Arriv_MIN3, on='mydata_MERGED', how='left')

Inter_Arriv_MAX3.columns = ['mydata_MERGED', 'Inter_Arriv_MAX']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Arriv_MAX3, on='mydata_MERGED', how='left')

Len_Mean3.columns = ['mydata_MERGED', 'Len_Mean']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Len_Mean3, on='mydata_MERGED', how='left')

Len_Var3.columns = ['mydata_MERGED', 'Len_Var']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Len_Var3, on='mydata_MERGED', how='left')

Len_MIN3.columns = ['mydata_MERGED', 'Len_MIN']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Len_MIN3, on='mydata_MERGED', how='left')

Len_MAX3.columns = ['mydata_MERGED', 'Len_MAX']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Len_MAX3, on='mydata_MERGED', how='left')

Inter_Len_Mean3.columns = ['mydata_MERGED', 'Inter_Len_Mean']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Len_Mean3, on='mydata_MERGED', how='left')

Inter_Len_Var3.columns = ['mydata_MERGED', 'Inter_Len_Var']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Len_Var3, on='mydata_MERGED', how='left')

Inter_Len_STD3.columns = ['mydata_MERGED', 'Inter_Len_STD']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Len_STD3, on='mydata_MERGED', how='left')

Inter_Len_MIN3.columns = ['mydata_MERGED', 'Inter_Len_MIN']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Len_MIN3, on='mydata_MERGED', how='left')

Inter_Len_MAX3.columns = ['mydata_MERGED', 'Inter_Len_MAX']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, Inter_Len_MAX3, on='mydata_MERGED', how='left')

MSS_Mean3.columns = ['mydata_MERGED', 'MSS_Mean']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, MSS_Mean3, on='mydata_MERGED', how='left')

MSS_Var3.columns = ['mydata_MERGED', 'MSS_Var']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, MSS_Var3, on='mydata_MERGED', how='left')

MSS_STD3.columns = ['mydata_MERGED', 'MSS_STD']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, MSS_STD3, on='mydata_MERGED', how='left')

MSS_MIN3.columns = ['mydata_MERGED', 'MSS_MIN']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, MSS_MIN3, on='mydata_MERGED', how='left')

MSS_MAX3.columns = ['mydata_MERGED', 'MSS_MAX']
MY_FEATURE_TABLE3 = pandas.merge(MY_FEATURE_TABLE3, MSS_MAX3, on='mydata_MERGED', how='left')

tmp9 = nvgt[['mydata_MERGED', 'Label']]
merged_inner = pandas.merge(MY_FEATURE_TABLE3, tmp9, on='mydata_MERGED', how='left')


#The next step consists on merging the feature table with ground truth in order to add a new columns called label.
# Through this column, each flow will have its own label and this will be used in the model training phase.
#The final result (feature matrix) is stored in dataset3.
dataset3 = merged_inner[merged_inner.columns[1:]].copy(deep=True)
dataset3 = dataset3[-dataset3['Label'].isnull()].copy(deep=True)

##################################################################################
# **************** Concatenate the two feature matrices  *************************
##################################################################################
#In this step, we will concatenate the two matrices previously created. The result is put in dataframe called "dat"
donnee = [dataset2, dataset3]
dat = pandas.concat(donnee)

##################################################################################
# *************************** Feature Importance  *********************************
##################################################################################
#In the next step, we will use Random Forest in order to select from all the features we calculated, which are the ones
#that are significant. This will reduce training times and provides better classification performances.
#By executing this function you can see a graph that will show the order of features according to their importance
# We extract only the features with the highest importance

# Split-out validation dataset

array = dat.values
X = array[:,0:28]
Y = array[:,28]

validation_size = 0.20
seed = 10
X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size, random_state=seed)

# Import `RandomForestClassifier`
from sklearn.ensemble import RandomForestClassifier

names = dat.columns

# Build the model
rfc = RandomForestClassifier()

# Fit the model
rfc.fit(X_train, Y_train)

# Print the results
print("Features sorted by their score:")
print(sorted(zip(map(lambda x: round(x, 28), rfc.feature_importances_),names), reverse=True))
# Import `pyplot` and `numpy`
import matplotlib.pyplot as plt
import numpy as np

# Isolate feature importances 
importance = rfc.feature_importances_

# Sort the feature importances 
sorted_importances = np.argsort(importance)

# Insert padding
padding = np.arange(len(names)-1) + 0.5

# Plot the data
plt.barh(padding, importance[sorted_importances], align='center')

# Customize the plot
plt.yticks(padding, names[sorted_importances])
plt.xlabel("Relative Importance")
plt.title("Variable Importance")

# Show the plot
plt.show()


##################################################################################
# **************************** Rebalancing step  *********************************
##################################################################################
#In this step you will set the number of flows to extract for each class of traffic in order to 
#ovoid the problem of majority and minority classes. Here it is set at 100, you will vary this number
#according to the assignement in order to see the influance that it has on the performance of classification algorithms.
#The result of this step is a dataframe named dat2.

lst_lb = []
for cnt1 in range(6):
    d = dat[dat['Label']==cnt1].iloc[:100].copy(deep=True)
    print(d.shape)
    lst_lb.append(d)
dat2 = pandas.concat(lst_lb)


##################################################################################
# **************************** Feature selection  *********************************
##################################################################################

#In this step, we will extract only significant features according to the results of Random Forest.
# The result is stored in the dataframe X_new
arrayy = dat2.values
Xy = arrayy[:,0:28] #The features
Yy = arrayy[:,28] # The labels

from sklearn.ensemble import ExtraTreesClassifier

from sklearn.feature_selection import SelectFromModel
clfy = RandomForestClassifier(200)
clfy = clfy.fit(Xy, Yy)
clfy.feature_importances_  

modely = SelectFromModel(clfy, prefit=True)
X_new = modely.transform(Xy)

# Here you can see the shape of the new dataframe that represents the features with significant information only.
X_new.shape   

##################################################################################
# ************************* Modeling and Prediction   ****************************
##################################################################################
#We split X_new representing the features and Y representing the label into X_train, and Y_train and X_validation, and Y_validation
# We use the training set (i.e., X_train, and Y_train) to train a model. 
#Then we give the X_validation to the trained model to predict the test labels. 
#The predicted values will be compared to the Y_validation in order to measure the efficiency of the classification.

validation_size = 0.20
seed = 150
X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X_new, Yy, test_size=validation_size, random_state=seed)


#Trining and classification using several models
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier 
from sklearn.ensemble import BaggingClassifier

########## Algorithm 1: Decision Tree classifier 
#Here we will use the library time in order to compute the training and testing times.

start_time = time.time()

#Training the SVM model using X_train and Y_train
DTclassifier= DecisionTreeClassifier (random_state=0)
DTclassifier.fit(X_train, Y_train)
print("---Training Time %s seconds ---" % (time.time() - start_time))

#Classification of X_validation using the SVM model
start_time = time.time()
predictions =  DTclassifier.predict(X_validation)

#Performance measure
#Here you will use the  classification report in order to extract the average F1 measure 
print(classification_report(Y_validation, predictions))
# You can see the classification performances through the confusion matrix as well.
print(confusion_matrix(Y_validation, predictions))
print("--- Testing Time %s seconds ---" % (time.time() - start_time))

########## Algorithm 2:  Random Forest Classifer
#Ensemble methods consists on training different algorithms with several samples, then combining using a certain method.
#approach, the obtained classifiers into one improved model to Several ensemble strategies exist.
#Voting, consists on applying several ML algorithms on samples. The experience results in a group of labels and 
#the final label is the one corresponding to the majority results or to the middle result. Although efficient, this
#method depends greatly on the number of classifiers used. 

#Create the model
start_time = time.time()
RFclassifier= RandomForestClassifier(n_estimators=100)

#Training the MLP model using X_train and Y_train
RFclassifier.fit(X_train, Y_train)
print("---Training Time %s seconds ---" % (time.time() - start_time))

#Classification of X_validation using the MLP model
start_time = time.time()
predictions =RFclassifier.predict(X_validation)
#Classification performances
print(classification_report(Y_validation, predictions))
print("--- Testing Time %s seconds ---" % (time.time() - start_time))

# You can see the classification performances through the confusion matrix as well.
print(confusion_matrix(Y_validation, predictions))


########## Algorithm 3:  Bagged Decision Trees for Classification

#Bagging, also called Boostrap algorithm consists on iteratively #extracting 
#groups of m samples from the training set, T times resulting in T #bootstrap 
#samples B1,B2,B3,… ,BT training T classifier,C1,C2,C3,…,CT.

#After which, a voting or averaging #method can be used in order to combine the 
#classifiers classification results. Finally, as its name implies, boosting
#algorithm consists on converting weak inducers to stronger ones by changing 
#the weights of training samples at the input.
#The instances are adjusted according to the previous error, thus #the weights 
#are set in order to reduce the classification error. 

# We will train several decision trees on different portions of the training set
# We will use a decision tree with 100 trees for more efficiency

#We create the decision tree classifier with 100 trees
base_estimator_bagging = DecisionTreeClassifier()
num_trees = 100

#We create the bagging model 
model = BaggingClassifier(base_estimator=base_estimator_bagging, n_estimators=num_trees, random_state=seed)

start_time = time.time()
#We train the model
model.fit(X_train, Y_train)
print("--- Training Time %s seconds ---" % (time.time() - start_time))

import time
start_time = time.time()
#We classify the traffic flows in X_validation
predictions=model.predict(X_validation)

# Classification performances : We can see the weighted average F1 score in the classification report
print(classification_report(Y_validation, predictions))
print("--- Testing %s seconds ---" % (time.time() - start_time))

# You can see the classification performances through the confusion matrix as well.
print(confusion_matrix(Y_validation, predictions))


# Unsupervised ML algorithm
#We will test whether an unsuppervised ML algorithm is more efficient than supervised MLs, and whether 
#it is adequate to actually deploy unsupervised algorithms for this dataset


###### 1. First scenario: K-means on the original dataset
scaler = StandardScaler()
scaled_features = scaler.fit_transform(Xy) 
from sklearn.preprocessing import StandardScaler    
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics.cluster import adjusted_rand_score
kmeans = KMeans(
    init="random",
    n_clusters=6,
    n_init=50,
    max_iter=600,
    random_state=42
)

kmeans.fit(scaled_features)

# The number of iterations required to converge
kmeans.n_iter_
len(kmeans.labels_)

print(classification_report(Yy, kmeans.labels_))
from sklearn.metrics.cluster import adjusted_rand_score
import seaborn as sns

ari1=adjusted_rand_score(Yy, kmeans.labels_)
silhouette1 = silhouette_score(Xy, kmeans.labels_).round(2)

### Print ARI and silhouette scores
print(ari1)
print(silhouette1)

### Plot correlation matrix (using all the feature, we have removed the label column)
f, ax = plt.subplots(figsize=(10, 8))
corr = dat[dat2.columns[0:28]].corr()
sns.heatmap(corr, mask=np.zeros_like(corr, dtype=np.bool), cmap=sns.diverging_palette(220, 10, as_cmap=True),
            square=True, ax=ax)

###### 2. second scenario: K-means using random forest
scaler = StandardScaler()
scaled_feature_news = scaler.fit_transform(X_new) 

kmeans_new = KMeans(
    init="random",
    n_clusters=8,
    n_init=50,
    max_iter=600,
    random_state=42
)

kmeans_new.fit(scaled_feature_news)

# The number of iterations required to converge
kmeans_new.n_iter_
len(kmeans_new.labels_)

ari2=adjusted_rand_score(Yy, kmeans_new.labels_)
silhouette2 = silhouette_score(scaled_feature_news, kmeans_new.labels_).round(2)

### Print ARI and silhouette scores
print(ari1)
print(silhouette1)

### Plot correlation matrix (using all the feature, we have removed the label column)

import seaborn as sns
### For more or for less features in X_new, adapt the below command

dataset = pandas.DataFrame({'Column1': X_new[:, 0], 'Column2': X_new[:, 1],'Column3': X_new[:, 2],'Column4': X_new[:, 3],'Column5': X_new[:, 4],'Column6': X_new[:, 5],'Column7': X_new[:, 6],'Column8': X_new[:, 7],'Column9': X_new[:, 8],'Column10': X_new[:, 9],'Column11': X_new[:, 10],'Column12': X_new[:, 11],'Column13': X_new[:, 12],'Column14': X_new[:, 13]})

f, ax = plt.subplots(figsize=(10, 8))
corr = dataset.corr()
sns.heatmap(corr, mask=np.zeros_like(corr, dtype=np.bool), cmap=sns.diverging_palette(220, 10, as_cmap=True),
            square=True, ax=ax)

###### 3. third scenario: K-means using PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
n_clusters=6
preprocessor = Pipeline(
    [
        ("scaler", MinMaxScaler()),
        ("pca", PCA(n_components=10, random_state=42)),
    ]
)
clusterer = Pipeline(
   [
       (
           "kmeans",
           KMeans(
               n_clusters=n_clusters,
               init="k-means++",
               n_init=50,
               max_iter=500,
               random_state=42,
           ),
       ),
   ]
)
pipe = Pipeline(
    [
        ("preprocessor", preprocessor),
        ("clusterer", clusterer)
    ]
)

pipe.fit(Xy)

preprocessed_data = pipe["preprocessor"].transform(Xy)
predicted_labels = pipe["clusterer"]["kmeans"].labels_

silhouette3=silhouette_score(preprocessed_data, predicted_labels)
ari3=adjusted_rand_score(Yy, predicted_labels)

print(ari3,silhouette3) 


