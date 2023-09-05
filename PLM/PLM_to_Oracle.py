import pyodbc  
import datetime, time
#import time
from snowflake.connector import connect
import csv
import shutil, os
import boto3
import cx_Oracle
from boto3.s3.transfer import S3Transfer
from datetime import datetime as dt
import os.path
from os import path
import subprocess
import pickle
import pandas as pd
import sys


config_path = "caxrpt@10.0.130.36:/home/caxrpt/reportdata/Engineering_application_config_file/config_PLM.py"
destination = "/home/ec2-user/PLM/"

p_5 = subprocess.Popen(["sudo","scp","-i","/home/caxrpt/.ssh/id_rsa",config_path,destination])
sts_5 = os.waitpid(p_5.pid, 0)

sys.path.append("/home/ec2-user/PLM")
import config_PLM as config1
config = config1.config



####################################################################################################
import sys
sys.path.append("/home/ec2-user/ERROR_LOGGER/ETL_LOGGER")
from logger import logger

sys.path.append("/home/ec2-user/CREDENTIAL/ALL_CREDENTIALS")
import credentials as cdtls

Logger = logger()
Logger.begin(process_name = 'PLM_TO_ORACLE')

try:
####################################################################################################
    Logger.start(log_info = 'Variables Prep')
####################################################################################################

    Curr_date_time = datetime.datetime.now()
    Curr_date_time_ms = Curr_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 
    Curr_date_time_ms_1 = Curr_date_time.strftime('%Y-%m-%d%H:%M:%S.%f')[:-3]
    Curr_date_only = Curr_date_time.strftime("%Y-%m-%d")
    #Curr_date_only_str  = str(Curr_date_only)

    print(f'current date time : {Curr_date_time_ms}')

    print(f'current date time modified : {Curr_date_time_ms_1}')

    print(f'Curr_date_only : {Curr_date_only}')

    COllID_COMP_INT = 1
    Roll_back = 'FALSE'

    # ------------------- Remmoving the files from the directory and stage  ----------------------

    # ---- Below is for temporary purpose ----- 
    # --------------------------
    now = datetime.datetime.now()
    print (f"start time:  {now}")

    Curr_year = Curr_date_time.year
    Curr_year_STR = str(Curr_year)

    dayoftheyear = Curr_date_time.timetuple().tm_yday
    Day_of_the_Year_STR = str(dayoftheyear)
    #Day_of_the_Year_rm_STR = str(dayoftheyear-2)

    len_Day_of_the_Year_STR = len(Day_of_the_Year_STR)

    if len_Day_of_the_Year_STR == 1:
        Day_of_the_Year_STR = '00'+Day_of_the_Year_STR
    elif len_Day_of_the_Year_STR == 2:
        Day_of_the_Year_STR = '0'+Day_of_the_Year_STR

    print(f'Day_of_the_Year_STR : {Day_of_the_Year_STR}')


    # Defining dates and year for previuos day
    prev_date_Day_of_the_Year_STR = str(dayoftheyear-1)
    prev_date_year_STR            = str(Curr_year)
    prev_day_date = datetime.date.today()-datetime.timedelta(1)

    print(f'prev_date_Day_of_the_Year_STR :{prev_date_Day_of_the_Year_STR}')
    print(f'prev_day_date : {prev_day_date}')

    len_Prev_Day_of_the_Year_STR = len(prev_date_Day_of_the_Year_STR)

    if len_Prev_Day_of_the_Year_STR == 1:
        prev_date_Day_of_the_Year_STR = '00'+prev_date_Day_of_the_Year_STR
    elif len_Day_of_the_Year_STR == 2:
        prev_date_Day_of_the_Year_STR = '0'+prev_date_Day_of_the_Year_STR

    print(f'Day_of_the_Year_STR : {Day_of_the_Year_STR}')


    #CAE Simlab project staging tables deletion

    DELETE_AAM_CAD_USER_DETAILS_STG = """DELETE FROM AAM_CAD_CAE_ECS_USER_DETAILS_STG WHERE APP_TYPE = 'PLM'"""

    DELETE_AAM_CAD_LICENSES_DETAILS_STG = """DELETE FROM AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG WHERE APP_TYPE = 'PLM'"""

    # Megging Simlab user staging table with final target table

    MERGE_AAM_CAD_USER_DETAILS = """
    MERGE INTO AAM_CAD_CAE_ECS_USER_DETAILS usrdtl USING 
    (SELECT USER_NAME
            ,USER_TYPE
            ,FILE_NAME
            ,APP_TYPE
            ,APP_NAME
    FROM AAM_CAD_CAE_ECS_USER_DETAILS_STG
    ) usrstg
    ON   (usrdtl.USER_NAME  =  usrstg.USER_NAME
    AND  usrdtl.USER_TYPE  =  usrstg.USER_TYPE
    AND  usrdtl.file_name  =  usrstg.FILE_NAME
    AND  usrdtl.APP_TYPE  =   usrstg.APP_TYPE
    AND  usrdtl.APP_NAME  =   usrstg.APP_NAME)
    when not matched then insert
    (LOGIN_DATE
     ,USER_NAME
     ,USER_TYPE
     ,file_name
     ,APP_TYPE
     ,APP_NAME
     ,CREATED_DATE
     ,CREATED_BY
     ,MODIFIED_DATE
     ,MODIFIED_BY
    )
    VALUES
    (TO_DATE('{0}','YYYY-MM-DD')
     ,usrstg.USER_NAME
     ,usrstg.USER_TYPE
     ,usrstg.FILE_NAME
     ,usrstg.APP_TYPE
     ,usrstg.APP_NAME
     ,SYSDATE
     ,'Back End Job'
     ,SYSDATE
     ,'Back End Job'
    )
    """

    # Megging Simlab license staging table with final target table

    MERGE_AAM_CAD_LICENSE_DETAILS = """
    MERGE INTO AAM_CAD_CAE_ECS_LICENSES_DETAILS licdtl USING
    (SELECT DATA_CAPTURE_DATE_TIME
            ,LICENSES_IN_USE
            ,LICENSES_AVAILABLE
            ,LICENSE_TYPE
            ,FILE_NAME
            ,APP_TYPE
            ,APP_NAME
    FROM AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG
    ) licstg
    ON   (licdtl.DATA_CAPTURE_DATE_TIME =  licstg.DATA_CAPTURE_DATE_TIME
    AND  licdtl.LICENSE_TYPE  =  licstg.LICENSE_TYPE
    AND  licdtl.file_name     =  licstg.FILE_NAME
    AND  licdtl.APP_TYPE      =  licstg.APP_TYPE
    AND  licdtl.APP_NAME      =  licstg.APP_NAME)
    when not matched then insert
    (DATA_CAPTURE_DATE_TIME
     ,DATA_CAPTURE_DATE
     ,LICENSES_IN_USE
     ,LICENSES_AVAILABLE
     ,LICENSE_TYPE
     ,FILE_NAME
     ,APP_TYPE
     ,APP_NAME
     ,CREATED_DATE
     ,CREATED_BY
     ,MODIFIED_DATE
     ,MODIFIED_BY
    )
    VALUES
    ( TO_DATE(TO_CHAR(licstg.DATA_CAPTURE_DATE_TIME,'DD-MON-YYYY HH24:MI'),'DD-MON-YYYY HH24:MI')
     ,to_char(licstg.DATA_CAPTURE_DATE_TIME,'DD-MON-YYYY')
     ,licstg.LICENSES_IN_USE
     ,licstg.LICENSES_AVAILABLE
     ,licstg.LICENSE_TYPE
     ,licstg.FILE_NAME
     ,licstg.APP_TYPE
     ,licstg.APP_NAME
     ,SYSDATE
     ,'Back End Job'
     ,SYSDATE
     ,'Back End Job'
    )
    """
    destination = "/home/ec2-user/CAD/ORACLE/FILES/"
    log_path = "/home/ec2-user/CAD/ORACLE/FILES/"

    all_sites = config.keys()
    for i in all_sites:
        for j in config[i].keys():
            now = datetime.datetime.now()
            print (f"start time:  {now}")
            Logger.start(log_info = f'runnig for user_type/license_type is = {j}')
            print(f'user_type or license_type is = {j}')
    
            f_usr =  config[i][j]['user']+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
            f_lic =  config[i][j]['license']+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
            
            file_user = config[i][j]['source']+f_usr
            file_lic = config[i][j]['source']+f_lic
            
            f_full_usr = log_path+f_usr
            f_full_license = log_path+f_lic
            
            # fetching fike from server
            p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_user,destination])
            sts_1 = os.waitpid(p_1.pid, 0)

            p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic,destination])
            sts_2 = os.waitpid(p_2.pid, 0)


            f_usr_rm =  config[i][j]['user']+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
            f_lic_rm =  config[i][j]['license']+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
            
            file_user_rm = config[i][j]['source']+f_usr_rm
            file_lic_rm = config[i][j]['source']+f_lic_rm

            f_full_usr_rm = log_path+f_usr_rm
            f_full_license_rm = log_path+f_lic_rm

                        
            p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_user_rm,destination])
            sts_3 = os.waitpid(p_3.pid, 0)

            p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_rm,destination])
            sts_4 = os.waitpid(p_4.pid, 0)

           # Defining target DB connection
            tns_dsn = cx_Oracle.makedsn(cdtls.oracle_bidwprd.host, cdtls.oracle_bidwprd.port, service_name=cdtls.oracle_bidwprd.service_name) 
            con_ORACLE = cx_Oracle.connect(user=cdtls.oracle_bidwprd.user, password=cdtls.oracle_bidwprd.password, dsn=tns_dsn) 

            cs_ORACLE = con_ORACLE.cursor()

            def convert_to_date(s):
                if s!='None':
                    year,month,day,hour,minute = s.split(':')
                    s = "TO_DATE('" + str(day) +'-' + str(month) + '-' + str(year) + ' ' + str(hour)+':'+str(minute) + "','DD-MM-YYYY HH24:MI')"
                return s

            try:
                cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
                cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)

                now = datetime.datetime.now()
                # Inserting data into user staging table

####################################################################################################
                Logger.start(log_info = 'Inserting Data Into User Staging Table')
####################################################################################################
                if os.path.isfile(f_full_usr) and os.path.getsize(f_full_usr) > 0:
                    user_type  =  j
                    app_type   =  'PLM'
                    app_name   =  i
                    data = pd.read_csv(f_full_usr, header=None)
                    if data.shape[0] > 0:
                        for index,row in data.iterrows():
                            user_name = row[0] ##date
                            try:
                                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+user_type+"','"+f_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                                INSERT_TABLE = cs_ORACLE.execute(sql)
                            except:
                                pass
                    else:
                        pass
                print ("Check 1.1")
                cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
                cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

                Logger.start(log_info = 'removing Data from User Staging Table')

                if os.path.isfile(f_full_usr_rm) and os.path.getsize(f_full_usr_rm) > 0:
                    user_type  =  j
                    app_type   =  'PLM'
                    app_name   =  i
                    data = pd.read_csv(f_full_usr_rm, header=None)
                    if data.shape[0]>0:
                        for index,row in data.iterrows():
                            user_name = row[0] ##date
                            try:
                                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+user_type+"','"+f_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                                INSERT_TABLE = cs_ORACLE.execute(sql)
                            except:
                                pass
                    else:
                        pass               
                cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))
                cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

####################################################################################################
                Logger.start(log_info = 'Inserting Data Into License Staging Table')
#################################################################################################### 
                
                if os.path.isfile(f_full_license) and os.path.getsize(f_full_license) > 0:
                    license_type  =  j
                    app_type   =  'PLM'
                    app_name   =  i
                    data = pd.read_csv(f_full_license, sep=' ', usecols=[0,1,2])
                    if data.shape[0]>0:
                        for index,row in data.iterrows():
                            date = row[0] ##date
                            license_used = row[1]
                            license_total = row[2]
                            try:
                                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic+"','"+str(app_type)+"','"+str(app_name)+"')" 
                                INSERT_TABLE = cs_ORACLE.execute(sql)
                            except:
                                pass
                    else:
                        pass

                if os.path.isfile(f_full_license_rm) and os.path.getsize(f_full_license_rm) > 0:
                    license_type  =  j
                    app_type   =  'PLM'
                    app_name   =  i
                    data = pd.read_csv(f_full_license_rm, sep=' ', usecols=[0,1,2])
                    if data.shape[0] > 0:
                        for index,row in data.iterrows():
                            date = row[0] ##date
                            license_used = row[1]
                            license_total = row[2]
                            try:
                                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                                INSERT_TABLE = cs_ORACLE.execute(sql)
                            except:
                                pass 
                    else:
                        pass
                cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
                
                cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
                print(' data insert in to DB')
                Logger.start(log_info = 'Inserting Data Into DB is Complete')
            except Exception as e:
                print('exception')
                ##############################
                Logger.update_error(error = e)
                ##############################
                print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
                Roll_back = 'TRUE'
                con_ORACLE.rollback()
            finally:
                if Roll_back == 'TRUE':
                    con_ORACLE.rollback()
                    cs_ORACLE.close()
                    con_ORACLE.close()
                    print('finally if')
                else:
                    con_ORACLE.commit()
                    print('done it')
                    cs_ORACLE.close()
                    con_ORACLE.close()
                now = datetime.datetime.now()
                print ("end time:",now.strftime("%Y-%m-%d %H:%M:%S"))

            client = boto3.client('s3', aws_access_key_id=cdtls.aws_s3.aws_access_key_id,aws_secret_access_key=cdtls.aws_s3.aws_secret_access_key)
            transfer = S3Transfer(client)
####################################################################################################
            Logger.start(log_info = 'Previous Day Users Files Transferred To AWS Location')
####################################################################################################
            if  ((path.exists(f_full_usr_rm)) and (path.exists(f_full_usr))):
                transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_rm, 'aam-nx-users-files-oracle',f_usr_rm)
                os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_rm)   

            if  ((path.exists(f_full_license_rm)) and (path.exists(f_full_license))):
                transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_rm, 'aam-nx-licenses-files-oracle',f_lic_rm)
                os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_rm)
####################################################################################################
except Exception as e:
    Logger.update_error(error=e)  
finally:
    Logger.end(email_alert=True, email_to=['1486ed74.aam.onmicrosoft.com@amer.teams.ms'])
####################################################################################################