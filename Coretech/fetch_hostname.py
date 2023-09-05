import pandas as pd
import socket
from time import sleep
import os
import glob
import warnings
import cx_Oracle
import datetime as dt
from datetime import datetime, timedelta,date
from os import path
import subprocess
import shutil, os
import sys


sys.path.append("/home/ec2-user/ERROR_LOGGER/ETL_LOGGER")
from logger import logger

Logger = logger()
Logger.begin(process_name = 'CORETECH')

server_path = '/home/cadrpt/reportdata/coretech/log/'
destination = "/home/ec2-user/AUTOCAD/CORETECH/log/"

filelist = [ f for f in os.listdir(destination) if f.endswith(".log") ]
print('existing filelist',filelist)
for f in filelist:
    os.remove(os.path.join(destination, f))
    print(' all existing log files from destination folder are deleted')

# fetch current date
# date_today = datetime.today().strftime('%Y-%m-%d')
# log_date = (date_today - timedelta(days=1)).strftime('%Y-%m-%d')
date_today = (date.today()- timedelta(days=1)).strftime("%Y-%m-%d")


p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",f"cadrpt@10.0.130.36:{server_path}CodeMeter{date_today}.log",destination])
sts_1 = os.waitpid(p_1.pid, 0)
print('file fetched and save to destination!!')

# get list if file for match datea
def file_list(date_today,all_csv_files):
    lst = []
    for sentence in  all_csv_files:
        if date_today in sentence:
            lst.append(sentence)
        else:
            pass
    return lst

def read_log_file(destination,file):

    # read txt file
    with open(destination+file) as file_in:
        lines = []
        for line in file_in:
            if 'Access over LAN' and 'to FC:PC:FC' in line:
                lines.append(line)

    # convert txt file to csv
    df = pd.DataFrame({'column':lines})
    df = df['column'].str.split(' ', expand=True)
    df = df[[0, 1, 6, 8]]
    print(df.head())
    return df

def pre_process(df):

    df1 = df[[0,1]]
    df1.columns = ['LOG_DATE','LOG_TIME'] 

    df2 = df[6].str.split('(', expand=True)
    df2.columns = ['IP_ADDRESS','HOSTNAME']

    list_data = [df2['HOSTNAME'].str.split("\\")[index][1]
                for index in range(0, len(df2))]
    df2['USER_ID'] = list_data
    df2['USER_ID'] = df2['USER_ID'].str.strip(')')
    df2 = df2[['IP_ADDRESS','USER_ID']]

    df3 = df[[8]]
    df3.columns = ['BUNDLE']
    df3 = df3['BUNDLE'].str.split(':', expand=True)
    df3 = df3[[3]]
    df3.columns = ['BUNDLE']

    return df1,df2,df3


# create database connection
def database_conn(user,password,service_name):
    tns_dsn = cx_Oracle.makedsn('aamlxbidbp001.aam.net', 1525, service_name=service_name)
    connction = cx_Oracle.connect(user=user, password=password, dsn=tns_dsn, encoding="UTF-8")
    cursor = connction.cursor()
    print('database connection successfully Done !')
    warnings.warn('Make Sure If work is done Please Close Database Connection !')
    return connction, cursor


bundle = {"1000":"3D_Evolution ",
            "1018":"AdvancedRepair",
            "1019":"Simplifier",
            "1020":"MetaFace",
            "1023":"Comparator",
            "1024":"Defeaturing",
            "1025":"MiddleFace",
            "1026":"AdvancedOffseting",
            "1027":"ThicknessChecker",
            "1028":"CollisionDetection",
            "1030":"Annotations&Markups",
            "1031":"MedusaLoad",
            "1033":"CADDSLoad",
            "1034":"CADDSSave",
            "1035":"CATIAV4Load",
            "1036":"CATIAV4Save",
            "1043":"CATIAV5Load",
            "1044":"CATIAV5CGRSave",
            "1047":"CATIAV5CGRLoad",
            "1048":"CATIAV5Save",
            "1051":"CATIAV5PluginSave",
            "1054":"EuclidE3ILoad",
            "1056":"AutocadDWGLoad",
            "1057":"AutocadDWGSave",
            "1058":"EuklidLoad",
            "1059":"EuklidSave",
            "1062":"IdeasArchiveLoad",
            "1069":"IGESLoad",
            "1070":"IGESSave",
            "1071":"InventorLoad",
            "1075":"InventorPluginSave",
            "1076":"JTLoad",
            "1077":"JTSave",
            "1078":"JTOpenAPILoad",
            "1079":"JTOpenAPISave",
            "1080":"NastranLoad",
            "1081":"NastranSave",
            "1082":"NXPart&AsmLoad",
            "1083":"NXPart&AsmSave",
            "1086":"NXPluginSave",
            "1087":"CreoLoad",
            "1089":"CreoNeutralLoad",
            "1090":"CreoNeutralSave",
            "1093":"CreoPluginSave",
            "1094":"RhinoLoad",
            "1095":"RhinoSave",
            "1096":"RobfaceLoad",
            "1097":"RobfaceSave",
            "1098":"SATLoad",
            "1099":"SATSave",
            "1102":"PLMXMLLoad",
            "1103":"PLMXMLSave",
            "1104":"SolidEdgeLoad",
            "1109":"SolidWorksLoad",
            "1110":"SolidWorksSave",
            "1113":"SolidWorksPlug.Save",
            "1114":"STEPLoad",
            "1115":"STEPSave",
            "1116":"STLLoad",
            "1117":"STLSave",
            "1118":"VDALoad",
            "1119":"VDASave",
            "1120":"VrmlLoad",
            "1121":"VrmlSave",
            "1124":"XTLoad",
            "1125":"XTSave",
            "1127":"3D-PDFSave",
            "1128":"VISILoad",
            "1130":"CATIAV6Load",
            "1132":"ShrinkWrap",
            "1133":"GeometricValidation",
            "1141":"MicrostationDGNLoad",
            "1142":"MicrostationDGNSave",
            "1149":"DraftAnalysis",
            "1150":"JtFilesChecker",
            "1151":"StepExtendedLoad",
            "1152":"StepExtendedSave",
            "1153":"AP242XmlLoad",
            "1154":"AP242XmlSave",
            "1155":"Modeling",
            "1156":"IFCLoad",
            "1157":"IFCSave",
            "1159":"AutodeskFBXLoad",
            "1160":"AutodeskFBXSave",
            "1163":"3MFLoad",
            "1164":"3MFSave",
            "1165":"AMFLoad",
            "1166":"AMFSave",
            "1167":"X3DLoad",
            "1168":"X3DSave",
            "1169":"Kinematics",
            "1170":"XGLLoad",
            "1171":"XGLSave",
            "1172":"COLLADALoad",
            "1173":"COLLADASave",
            "1174":"OBJLoad",
            "1175":"OBJSave",
            "1206":"JSonLoad",
            "1207":"JSonSave",
            "1214":"XPDMLoad",
            "1215":"XPDMSave",
            "1216":"GLTFLoad",
            "1217":"GLTFSave",
            "2000":"3D_Analyzer",
            "2018":"AdvancedRepair",
            "2023":"Comparator",
            "2027":"ThicknessChecker",
            "2028":"CollisionDetection",
            "2031":"MedusaLoad",
            "2033":"CADDSLoad",
            "2035":"CATIAV4Load",
            "2041":"CATIAV4FeatureLoad",
            "2043":"CATIAV5Load",
            "2045":"CATIAV5DrawingLoad",
            "2047":"CATIAV5CGRLoad",
            "2049":"CATIAV5FeatureLoad",
            "2054":"EuclidE3ILoad",
            "2056":"AutocadDWGLoad",
            "2058":"EuklidLoad",
            "2062":"IdeasArchiveLoad",
            "2064":"IdeasArcFeat.Load",
            "2069":"IGESLoad",
            "2071":"InventorLoad",
            "2076":"JTLoad",
            "2077":"JTSave",
            "2078":"JTOpenAPILoad",
            "2080":"NastranLoad",
            "2082":"NXPart&AsmLoad",
            "2084":"NXFeatureLoad",
            "2087":"CreoLoad",
            "2089":"CreoNeutralLoad",
            "2091":"CreoFeatureLoad",
            "2094":"RhinoLoad",
            "2096":"RobfaceLoad",
            "2098":"SATLoad",
            "2102":"PLMXMLLoad",
            "2104":"SolidEdgeLoad",
            "2109":"SolidWorksLoad",
            "2111":"SolidWorksFeat.Load",
            "2114":"STEPLoad",
            "2115":"STEPSave",
            "2116":"STLLoad",
            "2117":"STLSave",
            "2118":"VDALoad",
            "2120":"VrmlLoad",
            "2124":"XTLoad",
            "2127":"3D-PDFSave",
            "2128":"VISILoad",
            "2129":"CompositeData",
            "2130":"CATIAV6Load",
            "2131":"CATIAV6FeatureLoad",
            "2133":"GeometricValidation",
            "2134":"IdeasDrawingLoad",
            "2135":"NXDrawingLoad",
            "2137":"CreoDrawingLoad",
            "2139":"SolidWorksDraw.Load",
            "2141":"MicrostationDGNLoad",
            "2145":"CATIAV4DrawingLoad",
            "2148":"FeatureComparator",
            "2149":"DraftAnalysis",
            "2150":"JtFilesChecker",
            "2151":"StepExtendedLoad",
            "2152":"StepExtendedSave",
            "2153":"AP242XmlLoad",
            "2156":"IFCLoad",
            "2158":"CATIAV6DrawingLoad",
            "2159":"AutodeskFBXLoad",
            "2163":"3MFLoad",
            "2165":"AMFLoad",
            "2167":"X3DLoad",
            "2169":"Kinematics",
            "2170":"XGLLoad",
            "2172":"COLLADALoad",
            "2174":"OBJLoad",
            "2206":"JSonLoad",
            "2209":"DrawingRead",
            "2210":"DrawingWrite",
            "2211":"ConsistencyCheck",
            "2214":"XPDMLoad",
            "2216":"GLTFLoad"}


# store data to database table
def store_df_database(db_user,db_password,db_service_name,df):
    conn = None

    try:
        # create a connection object
        # get a cursor object from the connectio
        conn,cur = database_conn(db_user,db_password,db_service_name)
        # read dataframe from excel
        
        dataDf = df
        # prepare data insertion rows from dataframe
        dataInsertionTuples = [tuple(x) for x in dataDf.values]
        
        # create sql for data insertion
        
        sqlTxt = 'INSERT INTO AAM.CORETECH_LOG_DATA_STG\
                 ("LOG_DATE", "LOG_TIME", "IP_ADDRESS", "USER_ID", "BUNDLE", "HOST_NAME", "SITE_NAME", "BUNDLE_NAME","CREATED_BY","MODIFIED_DATE","MODIFIED_BY")\
                    VALUES (:0 , :1, :2, :3, :4, :5, :6, :7, :8, :9, :10)'
        
        print('sqlTxt',sqlTxt)
        
        mergeTxt = 'Merge Into AAM.CORETECH_LOG_DATA DC using (select * from AAM.CORETECH_LOG_DATA_STG) bar\
                    on (DC.LOG_DATE = bar.LOG_DATE and DC.LOG_TIME = bar.LOG_TIME and DC.IP_ADDRESS = bar.IP_ADDRESS and DC.USER_ID = bar.USER_ID)\
                        when matched then\
                            update \
                                set DC.BUNDLE = bar.BUNDLE,\
                                    DC.HOST_NAME = bar.HOST_NAME,\
                                    DC.SITE_NAME = bar.SITE_NAME,\
                                    DC.BUNDLE_NAME = bar.BUNDLE_NAME,\
                                    DC.CREATED_BY = bar.CREATED_BY,\
                                    DC.MODIFIED_DATE = bar.MODIFIED_DATE,\
                                    DC.MODIFIED_BY = bar.MODIFIED_BY\
                        when not matched then\
                            insert ( LOG_DATE,LOG_TIME,IP_ADDRESS,USER_ID,BUNDLE,HOST_NAME,SITE_NAME,BUNDLE_NAME,CREATED_BY,MODIFIED_DATE,MODIFIED_BY)\
                            values (bar.LOG_DATE,bar.LOG_TIME,bar.IP_ADDRESS,bar.USER_ID,bar.BUNDLE,bar.HOST_NAME,bar.SITE_NAME,bar.BUNDLE_NAME,bar.CREATED_BY,bar.MODIFIED_DATE,bar.MODIFIED_BY)'
        
        # execute the sql to perform data extraction
        cur.execute("delete from AAM.CORETECH_LOG_DATA_STG")
        print('table truncate complete')
        cur.executemany(sqlTxt, dataInsertionTuples, batcherrors=True)
        print('data insertion complete')
        cur.execute(mergeTxt)
        print('data merging complete')
        for error in cur.getbatcherrors():
            print("Error", error.message, "at row offset", error.offset)
            
        rowCount = cur.rowcount
        print("number of inserted rows =", rowCount)

        # commit the changes
        conn.commit()
    except Exception as err:
        print('Error while inserting rows into db')
        print(err)
    finally:
        if(conn):
            # close the cursor object to avoid memory leaks
            cur.close()
            # close the connection object also
            conn.close()
    
    print("data insert example execution complete!")
    return print("data insert example execution complete!")

try:
####################################################################################################
####################################################################################################
    Logger.start(log_info = 'CORETECH DATA Storing ')
####################################################################################################

    db_service_name= 'BIDWPRD.aam.net'
    db_user='PROD_AAM_RO'
    db_password='prodaamro'

    # path to read csv
    extension = 'log'
    os.chdir(destination)
    # get all csv file names
    all_txt_files = glob.glob('*.{}'.format(extension))
    txt_files = file_list(date_today,all_txt_files)
    print('all files',txt_files)

    if len(txt_files) > 0:
    
        for file in txt_files:
            try:
                df = read_log_file(destination,file)
                df1,df2,df3 = pre_process(df)
                dd = pd.concat([df1, df2.reindex(df1.index)], axis=1)
                final_df = pd.concat([dd, df3.reindex(dd.index)], axis=1)
                final_df.head()

                hostname = []
                for index, row in final_df.iterrows():
                    try:
                        host = socket.gethostbyaddr(row['IP_ADDRESS'])[0]
                        hostname.append(host)
                    except:
                        host = 'host name not found'
                        hostname.append(host)


                final_df['HOST_NAME'] = hostname
                final_df['SITE_NAME'] = final_df['HOST_NAME'].astype(str).str[:3]
                final_df['LOG_TIME'] = final_df['LOG_TIME'].astype(str).str[:8]
                final_df['BUNDLE_NAME'] = final_df['BUNDLE'].map(bundle)
                final_df1 = final_df[final_df['HOST_NAME']!='host name not found']
                final_df1 = final_df1[~final_df1['BUNDLE_NAME'].isnull()]
                final_df1['CREATED_BY'] = 'Back End Job'
                final_df1['MODIFIED_DATE'] = date_today    
                final_df1['MODIFIED_BY'] = 'Back End Job'
                final_df1 = final_df1.astype(str)

                print(final_df1.head())
            except:
                print('error at this file',file)
        store_df_database(db_user,db_password,db_service_name,final_df1)
    else:
        print('files not found')
        pass
####################################################################################################
except Exception as e:
    Logger.update_error(error=e)  
    print(e)
finally:
    Logger.end(email_alert=True, email_to=['1486ed74.aam.onmicrosoft.com@amer.teams.ms'])
####################################################################################################

