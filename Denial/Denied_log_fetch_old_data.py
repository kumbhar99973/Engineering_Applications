# Import statements 
import os
import pandas as pd
import numpy as np
import glob
import warnings
import cx_Oracle
from datetime import datetime, timedelta,date
import datetime
from os import path
import subprocess
import shutil, os
import sys

sys.path.append("/home/ec2-user/ERROR_LOGGER/ETL_LOGGER")
from logger import logger

Logger = logger()
Logger.begin(process_name = 'Denied LOG DATA')


rsa_key_path = "/home/cadrpt/.ssh/id_rsa"


def copy_files_matching_string(remote_path, local_path, match_string, rsa_key_path):
    # Create the scp command to copy the matched files to the local path, specifying the RSA key file
    scp_command = f"sudo scp -i {rsa_key_path} {remote_path}/*{match_string}* {local_path}"
    # Execute the scp command
    process = subprocess.Popen(scp_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for the process to finish and retrieve the output
    stdout, stderr = process.communicate()
    # Check the output for any errors
    if process.returncode != 0:
        print(f"An error occurred: {stderr.decode()}")
    else:
        print("Files copied successfully!")


def read_csv(path,filename):
    with open(path+filename, 'r') as temp_f:
        col_count = [ len(l.split(" ")) for l in temp_f.readlines() ]
        
    if len(col_count)>0:
        column_names = [i for i in range(0, max(col_count))]
        df = pd.read_csv(path+filename, header=None, delimiter=" ", names=column_names)
        return df
    else:
        pass


# create database connection
def database_conn(user,password,service_name):
    tns_dsn = cx_Oracle.makedsn('aamlxbidbd001.aam.net', 1521, service_name=service_name)
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
        
        sqlTxt = 'INSERT INTO AAM.Denied_log_stg\
                    (Log_date,Log_time,bundle,user_Id,hostname,reason,Filename,App_type,App_name_with_region)\
                    VALUES (:0 , :1, :2, :3, :4, :5, :6, :7, :8)'

        mergeTxt = 'Merge Into AAM.Denied_log DC using (select distinct * from AAM.Denied_log_stg) bar\
                    on (DC.Log_date = bar.Log_date and DC.Log_time = bar.Log_time and DC.bundle = bar.bundle and DC.user_Id = bar.user_Id and  DC.hostname = bar.hostname and DC.reason = bar.reason and DC.Filename = bar.Filename )\
                        when matched then\
                            update \
                                set DC.App_type = bar.App_type,\
                                    DC.App_name_with_region = bar.App_name_with_region\
                        when not matched then\
                            insert ( Log_date,Log_time,bundle,user_Id,hostname,reason,Filename,App_type,App_name_with_region)\
                            values (bar.Log_date,bar.Log_time,bar.bundle,bar.user_Id,bar.hostname,bar.reason,bar.Filename,bar.App_type,bar.App_name_with_region)'
        

        # execute the sql to perform data extraction
        cur.execute("delete from AAM.Denied_log_stg")
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
    
    return print("data insert for Denied Log execution complete!")


try:
####################################################################################################
####################################################################################################
    Logger.start(log_info = 'Denied DATA Storing ')
####################################################################################################

    # remove older files
    for app in ['ecs','plm','cad','cae']:
        destination = f"/home/ec2-user/AUTOCAD/DeniedLicense/{app}"
        filelist = [ f for f in os.listdir(destination) if f.endswith(".txt") ]
        # print('existing filelist',filelist)
        for f in filelist:
            os.remove(os.path.join(destination, f))
            print(' all existing txt files from destination folder are deleted')
    
    for dayoftheyear in range(115,222):
        # dayoftheyear = str(Curr_date_time.timetuple().tm_yday)
        len_Day_of_the_Year_STR = len(str(dayoftheyear))

        if len_Day_of_the_Year_STR == 1:
            dayoftheyear = '00'+dayoftheyear
        elif len_Day_of_the_Year_STR == 2:
            dayoftheyear = '0'+dayoftheyear
        
        for app in ['ecs','plm','cad','cae']:
            # define source and destination path
            source_path = f"cadrpt@10.0.130.36:/home/cadrpt/reportdata/license_denials/log/{app}"
            destination_path = f"/home/ec2-user/AUTOCAD/DeniedLicense/{app}"
            Curr_date_time = datetime.datetime.now()
            Curr_year = str(Curr_date_time.year)
            date_today = f"{Curr_year}-{dayoftheyear}"
            # print('date_today',date_today)
            print(f'Copying file for app:{app} and year-dayofyear:{date_today}')
            copy_files_matching_string(source_path, destination_path, date_today, rsa_key_path)
            print(f'Copying files are complete')

    for app in ['ecs','plm','cad','cae']:
    
        # define source and destination path
        destination_path = f"/home/ec2-user/AUTOCAD/DeniedLicense/{app}"
        os.chdir(r'/home/ec2-user/AUTOCAD/DeniedLicense/'+app+'')
        my_files = glob.glob('*.txt')

        final_df = pd.DataFrame()
        for filename in my_files:
            print(f'Runnnig for app:{app} file_name:{filename}')
            file_size = os.path.getsize(filename)
            if "DFMPRO" in filename:
                if file_size > 0:
                    # print('file name', filename)
                    cols = ['Log_date','Log_time','user_Id','hostname']
                    df = read_csv(destination_path,'/'+filename)
                    # print(f'{filename} shape is:{df.shape}')
                    if df.shape[0]>0:
                        df = df[[0,1,2,3]]
                        df.columns = cols
                        df['reason'] = "DFMPRO_not_available"
                        df['Filename'] = filename
                        df['bundle']  = "DFMPRO"
                        df = df[['Log_date','Log_time','bundle','user_Id','hostname','reason','Filename']]
                        df['App_type'] = app
                        final_df = pd.concat([final_df,df], ignore_index=True)
                else:
                    pass
            else:
                if file_size > 0:
                    cols = ['Log_date','Log_time','bundle','user_Id','hostname','reason']
                    # df = pd.read_csv(filename,sep=' ',header=None,error_bad_lines=False)
                    df =  read_csv(destination_path,'/'+filename)
                    # print(f'{filename} shape is:{df.shape}')
                    if (df.shape[0])> 0:
                        df['reason'] = df[df.columns[5:]].apply(lambda x: ' '.join(x.dropna().astype(str)),axis=1)
                        df = df[[0,1,2,3,4,'reason']]
                        df.columns = cols
                        df['Filename'] = filename
                        df['App_type'] = app
                        final_df = pd.concat([final_df,df], ignore_index=True)

        if (final_df.shape[0]) > 0:
            App_name_with_region = []
            for index, row in final_df.iterrows():
                apps = row['Filename'].split('_')[0]
                App_name_with_region.append(apps)
            
            final_df['App_name_with_region'] = App_name_with_region

            print('final_df shape',final_df.shape)
            db_service_name= 'BIDWDEV.aam.net'
            db_user='AAM'
            db_password='hdquowel'

            store_df_database(db_user,db_password,db_service_name,final_df)
            # path = f'/home/ec2-user/AUTOCAD/DeniedLicense/{app}.txt'

            # #export DataFrame to text file
            # with open(path, 'a') as f:
            #     df_string = final_df.to_string()
            #     f.write(df_string)


####################################################################################################
except Exception as e:
    Logger.update_error(error=e)  
    print(e)
finally:
    Logger.end(email_alert=True, email_to=['1486ed74.aam.onmicrosoft.com@amer.teams.ms'])
####################################################################################################