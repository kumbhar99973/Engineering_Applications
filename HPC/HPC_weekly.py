# import statements 
import os
import pandas as pd
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
Logger.begin(process_name = 'HPC LOG DATA DAILY AND WEEKLY')

server_path = '/home/caxrpt/reportdata/HPC_Reporting/HPC_Job_log/'
destination = "/home/ec2-user/AUTOCAD/HPC/"

filelist = [ f for f in os.listdir(destination) if f.endswith(".txt") ]
print('existing filelist',filelist)
for f in filelist:
    os.remove(os.path.join(destination, f))
    print(' all existing csv files from destination folder are deleted')

# fetch current date
date_today = (datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')
#date_today = date_today
#date_today = '2023-03-13'


# weekly files 
p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",f"cadrpt@10.0.130.36:{server_path}punlsf-hpc-weekly-logs-{date_today}.txt",destination])
sts_4 = os.waitpid(p_4.pid, 0)
p_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",f"cadrpt@10.0.130.36:{server_path}fralsf-hpc-weekly-logs-{date_today}.txt",destination])
sts_5 = os.waitpid(p_5.pid, 0)
p_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",f"cadrpt@10.0.130.36:{server_path}whqlsf-hpc-weekly-logs-{date_today}.txt",destination])
sts_6 = os.waitpid(p_6.pid, 0)


print('file fetched and save to destination!!')


def file_list(date_today,all_csv_files):
    lst = []
    for sentence in  all_csv_files:
        if date_today in sentence:
            lst.append(sentence)
        else:
            pass
    return lst

def clear_date(df):
    df_final = pd.DataFrame()
    for index, row in df.iterrows():
        try:
            row['SUBMITTED_TIME'] = datetime.strptime(row['SUBMITTED_TIME'],"%Y %b %d %H:%M:%S:")
            row['SUBMITTED_TIME'] = datetime.strftime(row['SUBMITTED_TIME'],"%Y %b %d %H:%M:%S:")
            row['RUNSTART_TIME'] = datetime.strptime(row['RUNSTART_TIME'],"%Y %b %d %H:%M:%S:")
            row['RUNSTART_TIME'] = datetime.strftime(row['RUNSTART_TIME'],"%Y %b %d %H:%M:%S:")
            row['COMPLETE_TIME'] = datetime.strptime(row['COMPLETE_TIME'],"%Y %b %d %H:%M:%S:")
            row['COMPLETE_TIME'] = datetime.strftime(row['COMPLETE_TIME'],"%Y %b %d %H:%M:%S:")
            df_final = df_final.append(row)
        except:
            pass
    return df_final


def read_txt(destination,date_today,file):
    colnames = ['JOBID', 'USERID', 'APPNAME', 'QUEUE', 'SUBMITTED_TIME', 'RUNSTART_TIME', 'COMPLETE_TIME', 'COMPLETE', 'CPU', 'STATUS']
    # read csv file for current date 
    df = pd.read_csv(destination+file,names=colnames,sep=',')
    try:
        df['FILENAME'] = file
        df['FILENAME_INI'] = file
        df['CREATED_BY'] = 'Back End Job'
        df['MODIFIED_DATE'] = date_today    
        df['MODIFIED_BY'] = 'Back End Job'
        df = clear_date(df)
        df = df.loc[:,['JOBID', 'USERID', 'APPNAME', 'QUEUE', 'SUBMITTED_TIME', 'RUNSTART_TIME', 'COMPLETE_TIME', 'COMPLETE', 'CPU', 'STATUS', 'FILENAME','FILENAME_INI' ,'CREATED_BY','MODIFIED_DATE','MODIFIED_BY']]
        df['JOBID'] = df['JOBID'].astype(int)
        df['CPU'] = df['CPU'].astype(int)
        print(' txt file reading complete')
        df = df.astype(str)
    except:
        print('error occure in file reading')
    return df

# create database connection
def database_conn(user,password,service_name):
    tns_dsn = cx_Oracle.makedsn('aamlxbidbp001.aam.net', 1525, service_name=service_name)
    connction = cx_Oracle.connect(user=user, password=password, dsn=tns_dsn, encoding="UTF-8")
    cursor = connction.cursor()
    print('database connection successfully Done !')
    warnings.warn('Make Sure If work is done Please Close Database Connection !')
    return connction, cursor


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
        
        sqlTxt = 'INSERT INTO AAM.CAD_HPC_Job_log_stg\
                    (JOBID, USERID, APPNAME, QUEUE, SUBMITTED_TIME, RUNSTART_TIME, COMPLETE_TIME, COMPLETE, CPU, STATUS, FILENAME,FILENAME_INI ,CREATED_BY,MODIFIED_DATE,MODIFIED_BY)\
                    VALUES (:0 , :1, :2, :3, :4, :5, :6, :7, :8, :9, :10,:11,:12,:13,:14)'


        mergeTxt = 'Merge Into AAM.CAD_HPC_Job_log DC using (select * from AAM.CAD_HPC_Job_log_stg) bar\
                    on (DC.USERID = bar.USERID and DC.APPNAME = bar.APPNAME and DC.QUEUE = bar.QUEUE and DC.SUBMITTED_TIME = bar.SUBMITTED_TIME \
                          and DC.RUNSTART_TIME = bar.RUNSTART_TIME and DC.COMPLETE_TIME = bar.COMPLETE_TIME and DC.COMPLETE = bar.COMPLETE and DC.CPU = bar.CPU and DC.STATUS = bar.STATUS )\
                        when matched then\
                            update \
                                set DC.JOBID = bar.JOBID,\
                                    DC.FILENAME = bar.FILENAME,\
                                    DC.FILENAME_INI = bar.FILENAME_INI,\
                                    DC.CREATED_BY = bar.CREATED_BY,\
                                    DC.MODIFIED_DATE = bar.MODIFIED_DATE,\
                                    DC.MODIFIED_BY = bar.MODIFIED_BY\
                        when not matched then\
                            insert ( JOBID, USERID, APPNAME, QUEUE, SUBMITTED_TIME, RUNSTART_TIME, COMPLETE_TIME, COMPLETE, CPU, STATUS, FILENAME,FILENAME_INI ,CREATED_BY,MODIFIED_DATE,MODIFIED_BY)\
                            values (bar.JOBID,bar.USERID,bar.APPNAME,bar.QUEUE,bar.SUBMITTED_TIME,bar.RUNSTART_TIME,bar.COMPLETE_TIME,bar.COMPLETE,bar.CPU,bar.STATUS,bar.FILENAME,bar.FILENAME_INI,bar.CREATED_BY,bar.MODIFIED_DATE,bar.MODIFIED_BY)'
        

        # execute the sql to perform data extraction
        cur.execute("delete from AAM.CAD_HPC_Job_log_stg")
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
    Logger.start(log_info = 'HPC DATA Storing ')
####################################################################################################

    db_service_name= 'BIDWPRD.aam.net'
    db_user='PROD_AAM_RO'
    db_password='prodaamro'

    # path to read csv
    extension = 'txt'
    os.chdir(destination)
    # get all csv file names
    all_txt_files = glob.glob('*.{}'.format(extension))

    txt_files = file_list(date_today,all_txt_files)

    new_df = pd.DataFrame()
    for file in txt_files:
        txt_file = read_txt(destination,date_today,file)
        print('txt_file shape',txt_file.shape)
        if txt_file.shape[0] > 0:
            txt_file = txt_file.astype(str)
            new_df = new_df.append(txt_file)
        else:
            pass
    final = new_df.drop_duplicates()
    print('final df shape is =', final.shape)
    store_df_database(db_user,db_password,db_service_name,final)

####################################################################################################
except Exception as e:
    Logger.update_error(error=e)  
    print(e)
finally:
    Logger.end(email_alert=True, email_to=['1486ed74.aam.onmicrosoft.com@amer.teams.ms'])
####################################################################################################