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
sys.path.append("/home/ec2-user/CREDENTIAL/ALL_CREDENTIALS")
import credentials as cdtls

####################################################################################################
import sys
sys.path.append("/home/ec2-user/ERROR_LOGGER/ETL_LOGGER")
from logger import logger

sys.path.append("/home/ec2-user/CREDENTIAL/ALL_CREDENTIALS")
import credentials as cdtls

Logger = logger()
Logger.begin(process_name = 'CAD_TO_ORACLE')
try:
####################################################################################################
####################################################################################################
    Logger.start(log_info = 'Variables Prep')
####################################################################################################

    Curr_date_time = datetime.datetime.now()
    Curr_date_time_ms = Curr_date_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 
    Curr_date_time_ms_1 = Curr_date_time.strftime('%Y-%m-%d%H:%M:%S.%f')[:-3]
    Curr_date_only = Curr_date_time.strftime("%Y-%m-%d")
    #Curr_date_only_str  = str(Curr_date_only)

    print('current date time :')
    print(Curr_date_time_ms)

    print('current date time modified :')
    print(Curr_date_time_ms_1)

    print('Curr_date_only :')
    print(Curr_date_only)

    COllID_COMP_INT = 1
    Roll_back = 'FALSE'

    # ------------------- Remmoving the files from the directory and stage  ----------------------

    #shutil.rmtree('/home/ec2-user/PARTWISEFILE')

    #os.mkdir('/home/ec2-user/PARTWISEFILE')

    # ---- Below is for temporary purpose ----- 
    # --------------------------
    now = datetime.datetime.now()
    print ("start time: ")

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

    print('Day_of_the_Year_STR')
    print(Day_of_the_Year_STR)

    #Curr_year   =  2019
    #Curr_year_STR  = '2019'


    #Day_of_the_Year_STR = '015'

    #Day_of_the_Year_rm_STR = '364'
    #print (now.strftime("%Y-%m-%d %H:%M:%S"))
    # ---- Temporary purpose ends -----


    # ------------- check Collection id completion query --------------

    #MAX_DATE_TIME = """SELECT MAX(DATA_MOVEMENT_TIMESTAMP) FROM AAM_PART_WISE_TOPSERIALNUMBER WHERE SITENAME = 'SMF' LIMIT 1; """


    #CAE Simlab project staging tables deletion

    DELETE_AAM_CAD_USER_DETAILS_STG = """DELETE FROM AAM_CAD_CAE_ECS_USER_DETAILS_STG WHERE APP_TYPE = 'CAD'"""

    DELETE_AAM_CAD_LICENSES_DETAILS_STG = """DELETE FROM AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG WHERE APP_TYPE = 'CAD'"""

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

    # Defining Source and destination paths for each application
    source = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/ptc/log/"
    source_US = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/catia/dsls/log/"
    source_NonUS = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/catia/chinaregion/log/"
    source_Solidworks = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/solidworks/log/"
    source_solidedge = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/solidedge/log/"
    source_autocad = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/autocad/log/"
    source_nx = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/nx/log/"
    source_dfmpro = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/DFMPro/log/"
    ##Source path added by Rajesh More on 16 June but is already exists
    ##source_NX_AdvanceDesigner_US = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/nx/log/"
    source_Catia_Zone_wise_Report  = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/catia/europe/log/"
    source_Germany = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/catia/germany/log/"
    source_PBO = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/catia/pbo/log/"
    source_US1 = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/catia/us/log/"
    source_PTC = "cadrpt@10.0.130.36:/home/cadrpt/reportdata/ptc/log/"
    

    destination = "/home/ec2-user/CAD/ORACLE/FILES/"
    log_path = "/home/ec2-user/CAD/ORACLE/FILES/"

    f_PTC_usr            = "ROCNT67-ptc-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_PTC_usr_mathcad    = "ROCNT67-ptc_mathcad-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    f_PTC_lincense       = "ROCNT67-ptc-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_PTC_lincense_mathcad= "ROCNT67-ptc_mathcad-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    f_PTC_usr_1            = "MetalDyne-PTC-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_PTC_usr_2    = "MetalDyne-PTC_MoldDesign-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    f_PTC_lincense_1         = "MetalDyne-PTC-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_PTC_lincense_2    = "MetalDyne-PTC_MoldDesign-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    
    myfile_1 = source+f_PTC_usr
    myfile_2 = source+f_PTC_usr_mathcad

    myfile_3 = source+f_PTC_lincense
    myfile_4 = source+f_PTC_lincense_mathcad

    myfile_5 = source+f_PTC_usr_1
    myfile_6 = source+f_PTC_usr_2

    myfile_7 = source+f_PTC_lincense_1
    myfile_8 = source+f_PTC_lincense_2
    
    f_PTC_full_usr                    = log_path+f_PTC_usr
    f_PTC_full_usr_mathcad            = log_path+f_PTC_usr_mathcad
    f_PTC_full_license                = log_path+f_PTC_lincense
    f_PTC_full_license_mathcad        = log_path+f_PTC_lincense_mathcad

    f_PTC_full_usr_1                    = log_path+f_PTC_usr_1
    f_PTC_full_usr_2            = log_path+f_PTC_usr_2
    f_PTC_full_license_1               = log_path+f_PTC_lincense_1
    f_PTC_full_license_2        = log_path+f_PTC_lincense_2
    
        
####################################################################################################
    Logger.start(log_info = 'Subprocess Scripts')
####################################################################################################

    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)

    p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_3,destination])
    sts_3 = os.waitpid(p_3.pid, 0)

    p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_4,destination])
    sts_4 = os.waitpid(p_4.pid, 0)

    p_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_5,destination])
    sts_5 = os.waitpid(p_5.pid, 0)

    p_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_6,destination])
    sts_6 = os.waitpid(p_6.pid, 0)

    p_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_7,destination])
    sts_7 = os.waitpid(p_7.pid, 0)

    p_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_8,destination])
    sts_8 = os.waitpid(p_8.pid, 0)
    
    # The beow code is for CATIA files

    f_CATIA_usr_US                  = "US_Sites-CATIA_V5-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_CATIA_usr_NonUS               = "China_Region-CATIA_V5-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    f_CATIA_lincense_US             = "US_Sites-CATIA_V5-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_CATIA_lincense_NonUS          = "China_Region-CATIA_V5-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_1 = source_US+f_CATIA_usr_US
    myfile_3 = source_NonUS+f_CATIA_usr_NonUS
    myfile_2 = source_US+f_CATIA_lincense_US
    myfile_4 = source_NonUS+f_CATIA_lincense_NonUS

    f_CATIA_full_usr_US                      = log_path+f_CATIA_usr_US
    f_CATIA_full_usr_NonUS                   = log_path+f_CATIA_usr_NonUS
    f_CATIA_full_license_US                  = log_path+f_CATIA_lincense_US
    f_CATIA_full_license_NonUS               = log_path+f_CATIA_lincense_NonUS


    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)

    p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_3,destination])
    sts_3 = os.waitpid(p_3.pid, 0)

    p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_4,destination])
    sts_4 = os.waitpid(p_4.pid, 0)


    # Loading files for Solidworks
    f_SOLIDWORKS_usr            = "AAM_US_WHQ-Solidworks-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_SOLIDWORKS_lincense       = "AAM_US_WHQ-Solidworks-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_1 = source_Solidworks+f_SOLIDWORKS_usr
    myfile_2 = source_Solidworks+f_SOLIDWORKS_lincense

    f_SOLIDWORKS_full_usr                    = log_path+f_SOLIDWORKS_usr
    f_SOLIDWORKS_full_license                = log_path+f_SOLIDWORKS_lincense

    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)

    # Loding SolidEdge files

    f_SOLIDEDGE_usr            = "Global_Sites-SolidEdge_ST9-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_SOLIDEDGE_lincense             = "Global_Sites-SolidEdge_ST9-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_1 = source_solidedge+f_SOLIDEDGE_usr
    myfile_2 = source_solidedge+f_SOLIDEDGE_lincense

    f_SOLIDEDGE_full_usr                    = log_path+f_SOLIDEDGE_usr
    f_SOLIDEDGE_full_license                = log_path+f_SOLIDEDGE_lincense

    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)

    f_ACAD_usr            = "US_Sites-AutoCAD_2018"+"-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_ACAD_INVPROSA_usr   = "US_Sites-INVPRO_RETR_2018"+"-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"


    f_ACAD_INVPROSA_INT_usr   = "International-INVENTOR_2018"+"-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt" # pankajaroa
    f_ACAD_INVPROSA_USCAMHCM_usr   = "US_Sites-InventorPro_CAM_HSM_2018"+"-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt" # pankajaroa

    f_ACAD_Mechanicl_usr  = "International-AutoCAD_Mechanical_2018"+"-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_ACAD_Electrical_usr = "US_Sites-AutoCAD_Electrical_2018"+"-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"


    # Below are for lincenses files
    f_ACAD_lincense             = "US_Sites-AutoCAD_2018"+"-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_ACAD_INVPROSA_lincense    = "US_Sites-INVPRO_RETR_2018"+"-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"


    f_ACAD_INVENTOR_INT_lincense        = "International-INVENTOR_2018"+"-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt" # pankajaroa
    f_ACAD_INVENTOR_USCAMHSM_lincense    = "US_Sites-InventorPro_CAM_HSM_2018"+"-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt" # pankajaroa


    f_ACAD_Mechanicl_lincense   = "International-AutoCAD_Mechanical_2018"+"-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_ACAD_Electrical_lincense  = "US_Sites-AutoCAD_Electrical_2018"+"-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_autocad_1 = source_autocad+f_ACAD_usr
    myfile_autocad_2 = source_autocad+f_ACAD_INVPROSA_usr

    myfile_autocad_3 = source_autocad+f_ACAD_Mechanicl_usr
    myfile_autocad_4 = source_autocad+f_ACAD_Electrical_usr

    myfile_autocad_5 = source_autocad+f_ACAD_lincense
    myfile_autocad_6 = source_autocad+f_ACAD_INVPROSA_lincense

    myfile_autocad_7 = source_autocad+f_ACAD_Mechanicl_lincense
    myfile_autocad_8 = source_autocad+f_ACAD_Electrical_lincense

    myfile_autocad_9 = source_autocad+f_ACAD_INVPROSA_INT_usr 
    myfile_autocad_10 = source_autocad+f_ACAD_INVPROSA_USCAMHCM_usr  

    myfile_autocad_11 = source_autocad+f_ACAD_INVENTOR_INT_lincense
    myfile_autocad_12 = source_autocad+f_ACAD_INVENTOR_USCAMHSM_lincense  

    f_ACAD_full_usr                    = log_path+f_ACAD_usr
    f_ACAD_full_INVPROSA_usr           = log_path+f_ACAD_INVPROSA_usr
    f_ACAD_full_Mechanicl_usr          = log_path+f_ACAD_Mechanicl_usr
    f_ACAD_full_Electrical_usr         = log_path+f_ACAD_Electrical_usr

    f_ACAD_full_INT_usr                = log_path+f_ACAD_INVPROSA_INT_usr  # pankajaroa
    f_ACAD_full_USCAMHUM_usr           = log_path+f_ACAD_INVPROSA_USCAMHCM_usr  # pankajaroa


    f_ACAD_full_license                = log_path+f_ACAD_lincense
    f_ACAD_full_INVPROSA_license       = log_path+f_ACAD_INVPROSA_lincense
    f_ACAD_full_Mechanicl_license      = log_path+f_ACAD_Mechanicl_lincense
    f_ACAD_full_Electrical_license     = log_path+f_ACAD_Electrical_lincense


    f_ACAD_full_INT_license            = log_path+f_ACAD_INVENTOR_INT_lincense  # pankajaroa
    f_ACAD_full_USCAMHSM_license       = log_path+f_ACAD_INVENTOR_USCAMHSM_lincense  # pankajaroa

    # The below code is added by Pankaj Arora on 14.01.2020


    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)

    p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_3,destination])
    sts_3 = os.waitpid(p_3.pid, 0)

    p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_4,destination])
    sts_4 = os.waitpid(p_4.pid, 0)

    p_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_5,destination])
    sts_5 = os.waitpid(p_5.pid, 0)

    p_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_6,destination])
    sts_6 = os.waitpid(p_6.pid, 0)

    p_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_7,destination])
    sts_7 = os.waitpid(p_7.pid, 0)

    p_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_8,destination])
    sts_8 = os.waitpid(p_8.pid, 0)


    p_9 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_9,destination])
    sts_9 = os.waitpid(p_9.pid, 0) # pankajaroa

    p_10 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_10,destination])
    sts_10 = os.waitpid(p_10.pid, 0) # pankajaroa

    p_11 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_11,destination])
    sts_11 = os.waitpid(p_11.pid, 0) # pankajaroa

    p_12 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_autocad_12,destination])
    sts_12 = os.waitpid(p_12.pid, 0) # pankajaroa

    # NX USer files

    f_usr_NX_Assemblies_US            = "US_Sites_rocnt67-NX_Assemblies-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_CheckMate_US             = "US_Sites_rocnt67-Checkmate-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Drafting_US              = "US_Sites_rocnt67-drafting-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_SolidModeling_US         = "US_Sites_rocnt67-solid_modeling-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_US                       = "US_Sites_rocnt67-NX-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Gateway_US               = "US_Sites_rocnt67-gateway-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Machining                = "NX_Machining_rocnt67-NX-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    ## Soruce_nx is same as that of source_NX_AdvanceDesigner_US hence I am adding the new files here
    f_usr_NX_ADVDES_US                = "US_Sites_rocnt67-ADVDES-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"  #Rajesh More 16 June 2021
    f_usr_NX_Designer_US              = "US_Sites_rocnt67-DESIGNER-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"  #Rajesh More 16 June 2021

    f_usr_NX_Assemblies_Global        = "Global_rocnt423-NX_Assemblies-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_CheckMate_Global         = "Global_rocnt423-Checkmate-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Drafting_Global          = "Global_rocnt423-drafting-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_SolidModeling_Global     = "Global_rocnt423-solid_modeling-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Global                   = "Global_rocnt423-NX-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Gateway_Global           = "Global_rocnt423-gateway-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Designer_Global          = "Global_rocnt423-DESIGNER-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"  #Rajesh More 16 June 2021
    f_usr_NX_AdvanceDesigner_Global   = "Global_rocnt423-ADVDES-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"  #Rajesh More 30 June 2021
    f_usr_NX_SC12500_US               = "US_Sites_rocnt67-SC12500-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_SC12500_US_Global        = "Global_rocnt423-SC12500-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_SC13500_US               = "US_Sites_rocnt67-SC13500-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_SC13500_US_Global        = "Global_rocnt423-SC13500-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_GMS4010                  = "US_Sites_rocnt67-GMS4010-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_NX11100N                 = "US_Sites_rocnt67-NX11100N-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_NX12100N                 = "US_Sites_rocnt67-NX12100N-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_NS5010_Global            = "Global_rocnt423-NS5010-NX12100N-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    # f_usr_NX_NS5010_US                = "US_Sites_rocnt67-NS5010-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_NX_Sheet_Metal_Global       = "Global_rocnt423-sheet_metal-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_PTC_US                      = "US_Sites-PTC_US-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_PTC_Global                  = "Global_sites-PTC_Global-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_PTC_Regional                = "Regional_Sites-PTC_Regional-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_usr_PTC_ToolDesign                = "Regional_Sites-PTC_ToolDesign-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"


    file_1 = source_nx+f_usr_NX_Assemblies_US
    file_2 = source_nx+f_usr_NX_CheckMate_US
    file_3 = source_nx+f_usr_NX_Drafting_US
    file_4 = source_nx+f_usr_NX_SolidModeling_US
    file_5 = source_nx+f_usr_NX_US
    file_6 = source_nx+f_usr_NX_Gateway_US
    file_7 = source_nx+f_usr_NX_Machining
    
    file_8 = source_nx+f_usr_NX_Assemblies_Global
    file_9 = source_nx+f_usr_NX_CheckMate_Global
    file_10 = source_nx+f_usr_NX_Drafting_Global
    file_11 = source_nx+f_usr_NX_SolidModeling_Global
    file_12 = source_nx+f_usr_NX_Global
    file_13 = source_nx+f_usr_NX_Gateway_Global
    
    file_14 = source_nx+f_usr_NX_ADVDES_US # Rajesh More 16 June 2021
    file_15 = source_nx+f_usr_NX_Designer_US # Rajesh More 16 June 2021
    file_16 = source_nx+f_usr_NX_Designer_Global # Rajesh More 16 June 2021
    file_17 = source_nx+f_usr_NX_AdvanceDesigner_Global # Rajesh More 30 June 2021
    file_18 = source_nx+f_usr_NX_SC12500_US
    file_19 = source_nx+f_usr_NX_SC12500_US_Global
    file_20 = source_nx+f_usr_NX_SC13500_US
    file_21 = source_nx+f_usr_NX_SC13500_US_Global
    file_22 = source_nx+f_usr_NX_GMS4010
    file_23 = source_nx+f_usr_NX_NX11100N
    file_24 = source_nx+f_usr_NX_NX12100N
    file_25 = source_nx+f_usr_NX_NS5010_Global
    # file_26 = source_nx+f_usr_NX_NS5010_US
    file_27 = source_nx+f_usr_NX_Sheet_Metal_Global

    file_28 = source_PTC+f_usr_PTC_US
    file_29 = source_PTC+f_usr_PTC_Global
    file_30 = source_PTC+f_usr_PTC_Regional
    file_31 = source_PTC+f_usr_PTC_ToolDesign





 
    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)

    p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_3,destination])
    sts_3 = os.waitpid(p_3.pid, 0)

    p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_4,destination])
    sts_4 = os.waitpid(p_4.pid, 0)

    p_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_5,destination])
    sts_5 = os.waitpid(p_5.pid, 0)

    p_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_6,destination])
    sts_6 = os.waitpid(p_6.pid, 0)

    p_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_7,destination])
    sts_7 = os.waitpid(p_7.pid, 0)

    p_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_8,destination])
    sts_8 = os.waitpid(p_8.pid, 0)

    p_9 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_9,destination])
    sts_9 = os.waitpid(p_9.pid, 0)

    p_10 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_10,destination])
    sts_10 = os.waitpid(p_10.pid, 0)

    p_11 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_11,destination])
    sts_11 = os.waitpid(p_11.pid, 0)

    p_12 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_12,destination])
    sts_12 = os.waitpid(p_12.pid, 0)

    p_13 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_13,destination])
    sts_13 = os.waitpid(p_13.pid, 0)

    p_14 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_14,destination])  # Rajesh More 16 June 2021
    sts_14 = os.waitpid(p_14.pid, 0)                                                             # Rajesh More 16 June 2021
    
    p_15 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_15,destination])  # Rajesh More 16 June 2021
    sts_15 = os.waitpid(p_15.pid, 0)                                                             # Rajesh More 16 June 2021

    p_16 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_16,destination])  # Rajesh More 16 June 2021
    sts_16 = os.waitpid(p_16.pid, 0)                                                             # Rajesh More 16 June 2021

    p_17 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_17,destination])  # Rajesh More 30 June 2021
    sts_17 = os.waitpid(p_17.pid, 0)                                                             # Rajesh More 30 June 2021

    p_18 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_18,destination])  
    sts_18 = os.waitpid(p_18.pid, 0)                   

    p_19 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_19,destination])  
    sts_19 = os.waitpid(p_19.pid, 0)   

    p_20 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_20,destination])  
    sts_20 = os.waitpid(p_20.pid, 0)   

    p_21 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_21,destination])  
    sts_21 = os.waitpid(p_21.pid, 0)   

    p_22 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_22,destination])  
    sts_22 = os.waitpid(p_22.pid, 0)   

    p_23 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_23,destination])  
    sts_23 = os.waitpid(p_23.pid, 0)   

    p_24 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_24,destination])  
    sts_24 = os.waitpid(p_24.pid, 0)   

    p_25 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_25,destination])  
    sts_25 = os.waitpid(p_25.pid, 0)   

#    p_26 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_26,destination])  
#    sts_26 = os.waitpid(p_26.pid, 0)   

    p_27 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_27,destination])  
    sts_27 = os.waitpid(p_27.pid, 0)   

    p_28 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_28,destination])  
    sts_28 = os.waitpid(p_28.pid, 0)  

    p_29 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_29,destination])  
    sts_29 = os.waitpid(p_29.pid, 0) 

    p_30 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_30,destination])  
    sts_30 = os.waitpid(p_30.pid, 0) 

    p_31 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_31,destination])  
    sts_31 = os.waitpid(p_31.pid, 0) 

    f_NX_full_usr_1           =  log_path+f_usr_NX_Assemblies_US
    f_NX_full_usr_2           =  log_path+f_usr_NX_CheckMate_US
    f_NX_full_usr_3           =  log_path+f_usr_NX_Drafting_US
    f_NX_full_usr_4           =  log_path+f_usr_NX_SolidModeling_US
    f_NX_full_usr_5           =  log_path+f_usr_NX_US
    f_NX_full_usr_6           =  log_path+f_usr_NX_Gateway_US
    f_NX_full_usr_7           =  log_path+f_usr_NX_Machining

    f_NX_full_usr_8           =  log_path+f_usr_NX_Assemblies_Global
    f_NX_full_usr_9           =  log_path+f_usr_NX_CheckMate_Global
    f_NX_full_usr_10          =  log_path+f_usr_NX_Drafting_Global
    f_NX_full_usr_11          =  log_path+f_usr_NX_SolidModeling_Global
    f_NX_full_usr_12          =  log_path+f_usr_NX_Global
    f_NX_full_usr_13          =  log_path+f_usr_NX_Gateway_Global

    f_NX_full_usr_14          =  log_path+f_usr_NX_ADVDES_US  # Rajesh More 16 June 2021
    f_NX_full_usr_15          =  log_path+f_usr_NX_Designer_US  # Rajesh More 16 June 2021
    f_NX_full_usr_16          =  log_path+f_usr_NX_Designer_Global  # Rajesh More 16 June 2021
    f_NX_full_usr_17          =  log_path+f_usr_NX_AdvanceDesigner_Global  # Rajesh More 16 June 2021
    f_NX_full_usr_18          =  log_path+f_usr_NX_SC12500_US  
    f_NX_full_usr_19          =  log_path+f_usr_NX_SC12500_US_Global
    f_NX_full_usr_20          =  log_path+f_usr_NX_SC13500_US  
    f_NX_full_usr_21          =  log_path+f_usr_NX_SC13500_US_Global
    f_NX_full_usr_22          =  log_path+f_usr_NX_GMS4010
    f_NX_full_usr_23          =  log_path+f_usr_NX_NX11100N
    f_NX_full_usr_24          =  log_path+f_usr_NX_NX12100N
    f_NX_full_usr_25          =  log_path+f_usr_NX_NS5010_Global
    # f_NX_full_usr_26          =  log_path+f_usr_NX_NS5010_US
    f_NX_full_usr_27          =  log_path+f_usr_NX_Sheet_Metal_Global
    f_PTC_full_usr_28         =  log_path+f_usr_PTC_US
    f_PTC_full_usr_29         =  log_path+f_usr_PTC_Global
    f_PTC_full_usr_30         =  log_path+f_usr_PTC_Regional
    f_PTC_full_usr_31         =  log_path+f_usr_PTC_ToolDesign





    f_lic_NX_Assemblies_US            = "US_Sites_rocnt67-NX_Assemblies-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_CheckMate_US             = "US_Sites_rocnt67-Checkmate-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Drafting_US              = "US_Sites_rocnt67-drafting-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_SolidModeling_US         = "US_Sites_rocnt67-solid_modeling-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_US                       = "US_Sites_rocnt67-NX-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Gateway_US               = "US_Sites_rocnt67-gateway-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Machining                = "NX_Machining_rocnt67-NX-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_ADVDES_US                = "US_Sites_rocnt67-ADVDES-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt" # Rajesh More 16 June 2021
    f_lic_NX_Designer_US              = "US_Sites_rocnt67-DESIGNER-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt" # Rajesh More 16 June 2021

    f_lic_NX_Assemblies_Global        = "Global_rocnt423-NX_Assemblies-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_CheckMate_Global         = "Global_rocnt423-Checkmate-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Drafting_Global          = "Global_rocnt423-drafting-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_SolidModeling_Global     = "Global_rocnt423-solid_modeling-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Global                   = "Global_rocnt423-NX-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Gateway_Global           = "Global_rocnt423-gateway-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Designer_Global          = "Global_rocnt423-DESIGNER-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"  # Rajesh More 16 June 2021
    f_lic_NX_AdvanceDesigner_Global   = "Global_rocnt423-ADVDES-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"  # Rajesh More 30 June 2021
    f_lic_NX_SC12500_US               = "US_Sites_rocnt67-SC12500-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_SC12500_US_Global        = "Global_rocnt423-SC12500-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"  
    f_lic_NX_SC13500_US               = "US_Sites_rocnt67-SC13500-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_SC13500_US_Global        = "Global_rocnt423-SC13500-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_GMS4010                  = "US_Sites_rocnt67-GMS4010-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_NX11100N                 = "US_Sites_rocnt67-NX11100N-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_NX12100N                 = "US_Sites_rocnt67-NX12100N-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_NS5010_Global            = "Global_rocnt423-NS5010-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    # f_lic_NX_NS5010_US                = "US_Sites_rocnt67-NS5010-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_lic_NX_Sheet_Metal_Global       = "Global_rocnt423-sheet_metal-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"       
    f_lic_PTC_US                      = "US_Sites-PTC_US-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"       
    f_lic_PTC_Global                  = "Global_sites-PTC_Global-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"      
    f_lic_PTC_Regional                = "Regional_Sites-PTC_Regional-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt" 
    f_lic_PTC_ToolDesign                = "Regional_Sites-PTC_ToolDesign-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"       
      
 

    file_lic_1 = source_nx+f_lic_NX_Assemblies_US
    file_lic_2 = source_nx+f_lic_NX_CheckMate_US
    file_lic_3 = source_nx+f_lic_NX_Drafting_US
    file_lic_4 = source_nx+f_lic_NX_SolidModeling_US
    file_lic_5 = source_nx+f_lic_NX_US
    file_lic_6 = source_nx+f_lic_NX_Gateway_US
    file_lic_7 = source_nx+f_lic_NX_Machining

    file_lic_8  = source_nx+f_lic_NX_Assemblies_Global
    file_lic_9  = source_nx+f_lic_NX_CheckMate_Global
    file_lic_10 = source_nx+f_lic_NX_Drafting_Global
    file_lic_11 = source_nx+f_lic_NX_SolidModeling_Global
    file_lic_12 = source_nx+f_lic_NX_Global
    file_lic_13 = source_nx+f_lic_NX_Gateway_Global

    file_lic_14 = source_nx+f_lic_NX_ADVDES_US  # Rajesh More 16 June 2021
    file_lic_15 = source_nx+f_lic_NX_Designer_US  # Rajesh More 16 June 2021
    file_lic_16 = source_nx+f_lic_NX_Designer_Global  # Rajesh More 16 June 2021
    file_lic_17 = source_nx+f_lic_NX_AdvanceDesigner_Global  # Rajesh More 30 June 2021
    file_lic_18 = source_nx+f_lic_NX_SC12500_US 
    file_lic_19 = source_nx+f_lic_NX_SC12500_US_Global
    file_lic_20 = source_nx+f_lic_NX_SC13500_US 
    file_lic_21 = source_nx+f_lic_NX_SC13500_US_Global
    file_lic_22 = source_nx+f_lic_NX_GMS4010
    file_lic_23 = source_nx+f_lic_NX_NX11100N
    file_lic_24 = source_nx+f_lic_NX_NX12100N
    file_lic_25 = source_nx+f_lic_NX_NS5010_Global
    # file_lic_26 = source_nx+f_lic_NX_NS5010_US
    file_lic_27 = source_nx+f_lic_NX_Sheet_Metal_Global
    file_lic_28 = source_PTC+f_lic_PTC_US
    file_lic_29 = source_PTC+f_lic_PTC_Global
    file_lic_30 = source_PTC+f_lic_PTC_Regional
    file_lic_31 = source_PTC+f_lic_PTC_ToolDesign

    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)

    p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_3,destination])
    sts_3 = os.waitpid(p_3.pid, 0)

    p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_4,destination])
    sts_4 = os.waitpid(p_4.pid, 0)

    p_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_5,destination])
    sts_5 = os.waitpid(p_5.pid, 0)

    p_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_6,destination])
    sts_6 = os.waitpid(p_6.pid, 0)

    p_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_7,destination])
    sts_7 = os.waitpid(p_7.pid, 0)

    p_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_8,destination])
    sts_8 = os.waitpid(p_8.pid, 0)

    p_9 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_9,destination])
    sts_9 = os.waitpid(p_9.pid, 0)

    p_10 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_10,destination])
    sts_10 = os.waitpid(p_10.pid, 0)

    p_11 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_11,destination])
    sts_11 = os.waitpid(p_11.pid, 0)

    p_12 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_12,destination])
    sts_12 = os.waitpid(p_12.pid, 0)

    p_13 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_13,destination])
    sts_13 = os.waitpid(p_13.pid, 0)

    p_14 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_14,destination])  # Rajesh More 16 Jun 2021
    sts_14 = os.waitpid(p_14.pid, 0)                                                                 # Rajesh More 16 Jun 2021

    p_15 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_15,destination])  # Rajesh More 16 Jun 2021
    sts_15 = os.waitpid(p_15.pid, 0)                                                                 # Rajesh More 16 Jun 2021

    p_16 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_16,destination])  # Rajesh More 16 Jun 2021
    sts_16 = os.waitpid(p_16.pid, 0)                                                                 # Rajesh More 16 Jun 2021

    p_17 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_17,destination])  # Rajesh More 30 Jun 2021
    sts_17 = os.waitpid(p_17.pid, 0)  
    
    
    p_18 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_18,destination])  
    sts_18 = os.waitpid(p_18.pid, 0)    

    p_19 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_19,destination])  
    sts_19 = os.waitpid(p_19.pid, 0)                                                             

    p_20 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_20,destination])  
    sts_20 = os.waitpid(p_20.pid, 0)  

    p_21 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_21,destination])  
    sts_21 = os.waitpid(p_21.pid, 0)  

    p_22 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_22,destination])  
    sts_22 = os.waitpid(p_22.pid, 0)

    p_23 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_23,destination])  
    sts_23 = os.waitpid(p_23.pid, 0)  

    p_24 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_24,destination])  
    sts_24 = os.waitpid(p_24.pid, 0)  

    p_25 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_25,destination])  
    sts_25 = os.waitpid(p_25.pid, 0)  
    
#    p_26 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_26,destination])  
#    sts_26 = os.waitpid(p_26.pid, 0) 

    p_27 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_27,destination])  
    sts_27 = os.waitpid(p_27.pid, 0)
    p_28 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_28,destination])  
    sts_28 = os.waitpid(p_28.pid, 0)
    p_29 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_29,destination])  
    sts_29 = os.waitpid(p_29.pid, 0)
    p_30 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_30,destination])  
    sts_30 = os.waitpid(p_30.pid, 0)
    p_31 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_lic_31,destination])  
    sts_31 = os.waitpid(p_31.pid, 0)

    f_NX_full_lic_1          =  log_path+f_lic_NX_Assemblies_US
    f_NX_full_lic_2          =  log_path+f_lic_NX_CheckMate_US
    f_NX_full_lic_3          =  log_path+f_lic_NX_Drafting_US
    f_NX_full_lic_4          =  log_path+f_lic_NX_SolidModeling_US
    f_NX_full_lic_5          =  log_path+f_lic_NX_US
    f_NX_full_lic_6          =  log_path+f_lic_NX_Gateway_US
    f_NX_full_lic_7          =  log_path+f_lic_NX_Machining

    f_NX_full_lic_8          =  log_path+f_lic_NX_Assemblies_Global
    f_NX_full_lic_9          =  log_path+f_lic_NX_CheckMate_Global
    f_NX_full_lic_10         =  log_path+f_lic_NX_Drafting_Global
    f_NX_full_lic_11         =  log_path+f_lic_NX_SolidModeling_Global
    f_NX_full_lic_12         =  log_path+f_lic_NX_Global
    f_NX_full_lic_13         =  log_path+f_lic_NX_Gateway_Global

    f_NX_full_lic_14         =  log_path+f_lic_NX_ADVDES_US  # Rajesh More 16 June 2021
    f_NX_full_lic_15         =  log_path+f_lic_NX_Designer_US  # Rajesh More 16 June 2021
    f_NX_full_lic_16         =  log_path+f_lic_NX_Designer_Global  # Rajesh More 16 June 2021
    f_NX_full_lic_17         =  log_path+f_lic_NX_AdvanceDesigner_Global  # Rajesh More 30 June 2021
    f_NX_full_lic_18         =  log_path+f_lic_NX_SC12500_US
    f_NX_full_lic_19         =  log_path+f_lic_NX_SC12500_US_Global
    f_NX_full_lic_20         =  log_path+f_lic_NX_SC13500_US
    f_NX_full_lic_21         =  log_path+f_lic_NX_SC13500_US_Global
    f_NX_full_lic_22         =  log_path+f_lic_NX_GMS4010
    f_NX_full_lic_23         =  log_path+f_lic_NX_NX11100N
    f_NX_full_lic_24         =  log_path+f_lic_NX_NX12100N
    f_NX_full_lic_25         =  log_path+f_lic_NX_NS5010_Global
    # f_NX_full_lic_26         =  log_path+f_lic_NX_NS5010_US
    f_NX_full_lic_27         =  log_path+f_lic_NX_Sheet_Metal_Global
    f_PTC_US_full_lic_28         =  log_path+f_lic_PTC_US
    f_PTC_US_full_lic_29         =  log_path+f_lic_PTC_Global
    f_PTC_US_full_lic_30         =  log_path+f_lic_PTC_Regional
    f_PTC_US_full_lic_31         =  log_path+f_lic_PTC_ToolDesign

    # Loading files for DFMPro
    f_DFMPro_usr            = "Global_sites-DFMPro_8-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_DFMPro_lincense       = "Global_sites-DFMPro_8-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_1 = source_dfmpro+f_DFMPro_usr
    myfile_2 = source_dfmpro+f_DFMPro_lincense

    f_DFMPro_full_usr                    = log_path+f_DFMPro_usr
    f_DFMPro_full_license                = log_path+f_DFMPro_lincense

    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_1,destination])
    sts_1 = os.waitpid(p_1.pid, 0)

    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_2,destination])
    sts_2 = os.waitpid(p_2.pid, 0)


###############################################################
#user

    f_NX_AS5050_US_usr                         = "US_Sites_rocnt67-AS5050-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_NS5010_Global_usr                     = "Global_rocnt423-NS5010-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_UGID105_US_usr                        = "US_Sites_rocnt67-UGID105-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_UGID100_US_usr                        = "US_Sites_rocnt67-UGID100-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_US_usr                  = "US_Sites_rocnt67-MFG-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_P1_US_usr                  = "US_Sites_rocnt67-P1-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

#license

    f_NX_AS5050_US_license                         = "US_Sites_rocnt67-AS5050-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_NS5010_Global_license                     = "Global_rocnt423-NS5010-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_UGID105_US_license                        = "US_Sites_rocnt67-UGID105-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_UGID100_US_license                        = "US_Sites_rocnt67-UGID100-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_US_license                  = "US_Sites_rocnt67-MFG-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_P1_US_license                  = "US_Sites_rocnt67-P1-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"


    myfile_NX_AS5050_US_usr = source_nx+f_NX_AS5050_US_usr
    myfile_NX_NS5010_Global_usr = source_nx+f_NX_NS5010_Global_usr
    myfile_NX_UGID105_US_usr = source_nx+f_NX_UGID105_US_usr
    myfile_NX_UGID100_US_usr = source_nx+f_NX_UGID100_US_usr
    myfile_NX_Manufacturing_US_usr = source_nx+f_NX_Manufacturing_US_usr
    myfile_NX_Manufacturing_P1_US_usr = source_nx+f_NX_Manufacturing_P1_US_usr
    myfile_NX_AS5050_US_license = source_nx+f_NX_AS5050_US_license
    myfile_NX_NS5010_Global_license = source_nx+f_NX_NS5010_Global_license
    myfile_NX_UGID105_US_license = source_nx+f_NX_UGID105_US_license
    myfile_NX_UGID100_US_license = source_nx+f_NX_UGID100_US_license
    myfile_NX_Manufacturing_US_license = source_nx+f_NX_Manufacturing_US_license
    myfile_NX_Manufacturing_P1_US_license = source_nx+f_NX_Manufacturing_P1_US_license

    myfile_NX_AS5050_US_usr_full = log_path+f_NX_AS5050_US_usr
    myfile_NX_NS5010_Global_usr_full = log_path+f_NX_NS5010_Global_usr
    myfile_NX_UGID105_US_usr_full = log_path+f_NX_UGID105_US_usr
    myfile_NX_UGID100_US_usr_full = log_path+f_NX_UGID100_US_usr
    myfile_NX_Manufacturing_US_usr_full = log_path+f_NX_Manufacturing_US_usr
    myfile_NX_Manufacturing_P1_US_usr_full = log_path+f_NX_Manufacturing_P1_US_usr
    myfile_NX_AS5050_US_license_full = log_path+f_NX_AS5050_US_license
    myfile_NX_NS5010_Global_license_full = log_path+f_NX_NS5010_Global_license
    myfile_NX_UGID105_US_license_full = log_path+f_NX_UGID105_US_license
    myfile_NX_UGID100_US_license_full = log_path+f_NX_UGID100_US_license
    myfile_NX_Manufacturing_US_license_full = log_path+f_NX_Manufacturing_US_license
    myfile_NX_Manufacturing_P1_US_license_full = log_path+f_NX_Manufacturing_P1_US_license


    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_AS5050_US_usr,destination])
    sts_1 = os.waitpid(p_1.pid, 0)
    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_NS5010_Global_usr,destination])
    sts_2 = os.waitpid(p_2.pid, 0)	
    p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID105_US_usr,destination])
    sts_3 = os.waitpid(p_3.pid, 0)	
    p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID100_US_usr,destination])
    sts_4 = os.waitpid(p_4.pid, 0)	
    p_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_US_usr,destination])
    sts_5 = os.waitpid(p_5.pid, 0)	
    p_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_P1_US_usr,destination])
    sts_6 = os.waitpid(p_6.pid, 0)	
    p_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_AS5050_US_license,destination])
    sts_7 = os.waitpid(p_7.pid, 0)		
    p_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_NS5010_Global_license,destination])
    sts_8 = os.waitpid(p_8.pid, 0)		
    p_9 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID105_US_license,destination])
    sts_9 = os.waitpid(p_9.pid, 0)		
    p_10 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID100_US_license,destination])
    sts_10 = os.waitpid(p_10.pid, 0)
    p_11 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_US_license,destination])
    sts_11 = os.waitpid(p_11.pid, 0)
    p_12 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_P1_US_license,destination])
    sts_12 = os.waitpid(p_12.pid, 0)	


#user

    f_All_Autodesk_Products_usr                  = "All-Autodesk_Apps-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_Autocad_Electrical_Mechanical_usr          = "All-AutoCAD_Apps-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_Inventor_Inventor_Pro_usr                  = "All-InventorPro_Apps-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

#license

    f_All_Autodesk_Products_license                  = "All-Autodesk_Apps-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_Autocad_Electrical_Mechanical_license          = "All-AutoCAD_Apps-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_Inventor_Inventor_Pro_license                  = "All-InventorPro_Apps-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"


    myfile_All_Autodesk_Products_usr = source_autocad+f_All_Autodesk_Products_usr
    myfile_Autocad_Electrical_Mechanical_usr = source_autocad+f_Autocad_Electrical_Mechanical_usr
    myfile_Inventor_Inventor_Pro_usr = source_autocad+f_Inventor_Inventor_Pro_usr
    myfile_All_Autodesk_Products_license = source_autocad+f_All_Autodesk_Products_license
    myfile_Autocad_Electrical_Mechanical_license = source_autocad+f_Autocad_Electrical_Mechanical_license
    myfile_Inventor_Inventor_Pro_license = source_autocad+f_Inventor_Inventor_Pro_license    


    myfile_All_Autodesk_Products_usr_full = log_path+f_All_Autodesk_Products_usr
    myfile_Autocad_Electrical_Mechanical_usr_full = log_path+f_Autocad_Electrical_Mechanical_usr
    myfile_Inventor_Inventor_Pro_usr_full = log_path+f_Inventor_Inventor_Pro_usr
    myfile_All_Autodesk_Products_license_full = log_path+f_All_Autodesk_Products_license
    myfile_Autocad_Electrical_Mechanical_license_full = log_path+f_Autocad_Electrical_Mechanical_license
    myfile_Inventor_Inventor_Pro_license_full = log_path+f_Inventor_Inventor_Pro_license    


    p_13 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_All_Autodesk_Products_usr,destination])
    sts_13 = os.waitpid(p_13.pid, 0)	
    p_14 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Autocad_Electrical_Mechanical_usr,destination])
    sts_14 = os.waitpid(p_14.pid, 0)	
    p_15 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Inventor_Inventor_Pro_usr,destination])
    sts_15 = os.waitpid(p_15.pid, 0)
    p_16 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_All_Autodesk_Products_license,destination])
    sts_16 = os.waitpid(p_16.pid, 0)	
    p_17 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Autocad_Electrical_Mechanical_license,destination])
    sts_17 = os.waitpid(p_17.pid, 0)
    p_18 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Inventor_Inventor_Pro_license,destination])
    sts_18 = os.waitpid(p_18.pid, 0)	
###############################################################
# Code by SM

    f_NX_usr          = "PBO-NX93100-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_NX_license      = "PBO-NX93100-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_19 = source_nx + f_NX_usr
    myfile_20 = source_nx + f_NX_license
    
    f_NX_full_usr_19 = log_path+f_NX_usr
    f_NX_full_license_20 = log_path+f_NX_license
    
    p_19 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_19,destination])
    sts_19 = os.waitpid(p_19.pid, 0)
    
    p_20 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_20,destination])
    sts_20 = os.waitpid(p_20.pid, 0)
    
    #Catia Zone wise Report
    
    f_Catia_Zone_wise_Report_usr = "Europe_Sites-CATIA_V5-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_Catia_Zone_wise_Report_license = "Europe_Sites-CATIA_V5-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    
    myfile_21 = source_Catia_Zone_wise_Report + f_Catia_Zone_wise_Report_usr
    myfile_22 = source_Catia_Zone_wise_Report + f_Catia_Zone_wise_Report_license
    
    f_Catia_Zone_wise_Report_full_usr_21 = log_path+f_Catia_Zone_wise_Report_usr
    f_Catia_Zone_wise_Report_full_license_22 = log_path+f_Catia_Zone_wise_Report_license
    
    p_21 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_21,destination])
    sts_21 = os.waitpid(p_21.pid, 0)
    
    p_22 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_22,destination])
    sts_22 = os.waitpid(p_22.pid, 0)
    
    # Germany*****************
    f_Germany_usr     = "Germany_Sites-CATIA_V5-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_Germany_license      = "Germany_Sites-CATIA_V5-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_23 = source_Germany + f_Germany_usr
    myfile_24 = source_Germany + f_Germany_license
    
    f_Germany_full_usr_23 = log_path+f_Germany_usr
    f_Germany_full_license_24 = log_path+f_Germany_license
    
    p_23 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_23,destination])
    sts_23 = os.waitpid(p_23.pid, 0)
    
    p_24 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_24,destination])
    sts_24 = os.waitpid(p_24.pid, 0)
    
    # PBO ****************************************
    f_PBO_usr     = "PBO_Sites-CATIA_V5-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_PBO_license      = "PBO_Sites-CATIA_V5-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_25 = source_PBO + f_PBO_usr
    myfile_26 = source_PBO + f_PBO_license
    
    f_PBO_full_usr_25 = log_path+f_PBO_usr
    f_PBO_full_license_26 = log_path+f_PBO_license
    
    p_25 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_25,destination])
    sts_25 = os.waitpid(p_25.pid, 0)
    
    p_26 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_26,destination])
    sts_26 = os.waitpid(p_26.pid, 0)
    
    # US1 ***************************************
    f_US1_usr     = "US1_Sites-CATIA_V5-users-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"
    f_US1_license      = "US1_Sites-CATIA_V5-licenses-"+Curr_year_STR+"-"+Day_of_the_Year_STR+".txt"

    myfile_27 = source_US1 + f_US1_usr
    myfile_28 = source_US1 + f_US1_license
    
    f_US1_full_usr_27 = log_path+f_US1_usr
    f_US1_full_license_28 = log_path+f_US1_license
    
    p_27 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_27,destination])
    sts_27 = os.waitpid(p_27.pid, 0)
    
    p_28 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_28,destination])
    sts_28 = os.waitpid(p_28.pid, 0)

###############################################################

    # Defining dates and year for previuos day
    prev_date_Day_of_the_Year_STR = str(dayoftheyear-1)
    prev_date_year_STR            = str(Curr_year)
    prev_day_date = datetime.date.today()-datetime.timedelta(1)

    print('prev_date_Day_of_the_Year_STR')
    print(prev_date_Day_of_the_Year_STR)
    print('prev_day_date')
    print(prev_day_date)

    len_Prev_Day_of_the_Year_STR = len(prev_date_Day_of_the_Year_STR)

    if len_Prev_Day_of_the_Year_STR == 1:
        prev_date_Day_of_the_Year_STR = '00'+prev_date_Day_of_the_Year_STR
    elif len_Day_of_the_Year_STR == 2:
        prev_date_Day_of_the_Year_STR = '0'+prev_date_Day_of_the_Year_STR

    print('Day_of_the_Year_STR')
    print(Day_of_the_Year_STR)

    #prev_date_Day_of_the_Year_STR = '014'

    f_PTC_usr_rm       = "ROCNT67-ptc-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_PTC_usr_mathcad_rm     = "ROCNT67-ptc_mathcad-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_PTC_lincense_rm  = "ROCNT67-ptc-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_PTC_lincense_mathcad_rm  = "ROCNT67-ptc_mathcad-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"


    f_PTC_usr_1_rm            = "MetalDyne-PTC-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_PTC_usr_2_rm    = "MetalDyne-PTC_MoldDesign-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_PTC_lincense_1_rm         = "MetalDyne-PTC-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_PTC_lincense_2_rm    = "MetalDyne-PTC_MoldDesign-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_PTC_full_usr_rm               = log_path+f_PTC_usr_rm
    f_PTC_full_usr_mathcad_rm       = log_path+f_PTC_usr_mathcad_rm


    f_PTC_full_license_rm           = log_path+f_PTC_lincense_rm
    f_PTC_full_license_mathcad_rm   = log_path+f_PTC_lincense_mathcad_rm


    f_PTC_full_usr_1_rm                    = log_path+f_PTC_usr_1_rm
    f_PTC_full_usr_2_rm            = log_path+f_PTC_usr_2_rm

    f_PTC_full_license_1_rm               = log_path+f_PTC_lincense_1_rm
    f_PTC_full_license_2_rm        = log_path+f_PTC_lincense_2_rm

    myfile_rm_1 = source+f_PTC_usr_rm
    myfile_rm_2 = source+f_PTC_usr_mathcad_rm

    myfile_rm_3 = source+f_PTC_lincense_rm
    myfile_rm_4 = source+f_PTC_lincense_mathcad_rm


    myfile_rm_5 = source+f_PTC_usr_1_rm
    myfile_rm_6 = source+f_PTC_usr_2_rm

    myfile_rm_7 = source+f_PTC_lincense_1_rm
    myfile_rm_8 = source+f_PTC_lincense_2_rm
    
    p_rm_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_1,destination])
    sts_rm_1 = os.waitpid(p_rm_1.pid, 0)

    p_rm_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_2,destination])
    sts_rm_2 = os.waitpid(p_rm_2.pid, 0)

    p_rm_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_3,destination])
    sts_rm_3 = os.waitpid(p_rm_3.pid, 0)

    p_rm_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_4,destination])
    sts_rm_4 = os.waitpid(p_rm_4.pid, 0)

    p_rm_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_5,destination])
    sts_rm_5 = os.waitpid(p_rm_5.pid, 0)

    p_rm_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_6,destination])
    sts_rm_6 = os.waitpid(p_rm_6.pid, 0)

    p_rm_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_7,destination])
    sts_rm_7 = os.waitpid(p_rm_7.pid, 0)

    p_rm_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_8,destination])
    sts_rm_8 = os.waitpid(p_rm_8.pid, 0)
     
    # CATIA previous day file upload_file

    f_CATIA_usr_US_rm       = "US_Sites-CATIA_V5-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_CATIA_usr_NonUS_rm    = "China_Region-CATIA_V5-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_CATIA_lincense_US_rm     = "US_Sites-CATIA_V5-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_CATIA_lincense_NonUS_rm  = "China_Region-CATIA_V5-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_CATIA_full_usr_US_rm               = log_path+f_CATIA_usr_US_rm
    f_CATIA_full_usr_NonUS_rm            = log_path+f_CATIA_usr_NonUS_rm
    f_CATIA_full_license_US_rm           = log_path+f_CATIA_lincense_US_rm
    f_CATIA_full_license_NonUS_rm        = log_path+f_CATIA_lincense_NonUS_rm

    myfile_rm_1 = source_US+f_CATIA_usr_US_rm
    myfile_rm_3 = source_NonUS+f_CATIA_usr_NonUS_rm
    myfile_rm_2 = source_US+f_CATIA_lincense_US_rm
    myfile_rm_4 = source_NonUS+f_CATIA_lincense_NonUS_rm

    p_rm_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_1,destination])
    sts_rm_1 = os.waitpid(p_rm_1.pid, 0)

    p_rm_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_2,destination])
    sts_rm_2 = os.waitpid(p_rm_2.pid, 0)

    p_rm_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_3,destination])
    sts_rm_3 = os.waitpid(p_rm_3.pid, 0)

    p_rm_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_4,destination])
    sts_rm_4 = os.waitpid(p_rm_4.pid, 0)

    # Previous day file load for Solidworks
    f_SOLIDWORKS_usr_rm       = "AAM_US_WHQ-Solidworks-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_SOLIDWORKS_lincense_rm  = "AAM_US_WHQ-Solidworks-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_SOLIDWORKS_full_usr_rm               = log_path+f_SOLIDWORKS_usr_rm
    f_SOLIDWORKS_full_license_rm           = log_path+f_SOLIDWORKS_lincense_rm

    myfile_rm_1 = source_Solidworks+f_SOLIDWORKS_usr_rm
    myfile_rm_2 = source_Solidworks+f_SOLIDWORKS_lincense_rm

    p_rm_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_1,destination])
    sts_rm_1 = os.waitpid(p_rm_1.pid, 0)

    p_rm_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_2,destination])
    sts_rm_2 = os.waitpid(p_rm_2.pid, 0)

    # Previous day SolidEdge loading file

    f_SOLIDEDGE_usr_rm       = "Global_Sites-SolidEdge_ST9-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_SOLIDEDGE_lincense_rm  = "Global_Sites-SolidEdge_ST9-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_SOLIDEDGE_full_usr_rm               = log_path+f_SOLIDEDGE_usr_rm
    f_SOLIDEDGE_full_license_rm           = log_path+f_SOLIDEDGE_lincense_rm

    myfile_rm_1 = source_solidedge+f_SOLIDEDGE_usr_rm
    myfile_rm_2 = source_solidedge+f_SOLIDEDGE_lincense_rm

    p_rm_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_1,destination])
    sts_rm_1 = os.waitpid(p_rm_1.pid, 0)

    p_rm_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_2,destination])
    sts_rm_2 = os.waitpid(p_rm_2.pid, 0)

    # Processing previous day files

    f_ACAD_usr_rm            = "US_Sites-AutoCAD_2018"+"-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_ACAD_INVPROSA_usr_rm   = "US_Sites-INVPRO_RETR_2018"+"-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_ACAD_INVPROSA_INT_usr_rm        = "International-INVENTOR_2018"+"-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt" # pankajaroa
    f_ACAD_INVPROSA_USCAMHCM_usr_rm   = "US_Sites-InventorPro_CAM_HSM_2018"+"-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt" # pankajaroa

    f_ACAD_Mechanicl_usr_rm  = "International-AutoCAD_Mechanical_2018"+"-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_ACAD_Electrical_usr_rm = "US_Sites-AutoCAD_Electrical_2018"+"-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_ACAD_lincense_rm             = "US_Sites-AutoCAD_2018"+"-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_ACAD_INVPROSA_lincense_rm    = "US_Sites-INVPRO_RETR_2018"+"-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_ACAD_INVENTOR_INT_lincense_rm         = "International-INVENTOR_2018"+"-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt" # pankajaroa
    f_ACAD_INVENTOR_USCAMHSM_lincense_rm    = "US_Sites-InventorPro_CAM_HSM_2018"+"-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt" # pankajaroa

    f_ACAD_Mechanicl_lincense_rm   = "International-AutoCAD_Mechanical_2018"+"-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_ACAD_Electrical_lincense_rm   = "US_Sites-AutoCAD_Electrical_2018"+"-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"


    # Removing file complete path

    f_ACAD_full_usr_rm                    = log_path+f_ACAD_usr_rm
    f_ACAD_full_INVPROSA_usr_rm           = log_path+f_ACAD_INVPROSA_usr_rm
    f_ACAD_full_Mechanicl_usr_rm          = log_path+f_ACAD_Mechanicl_usr_rm
    f_ACAD_full_Electrical_usr_rm         = log_path+f_ACAD_Electrical_usr_rm

    f_ACAD_full_INT_usr_rm                = log_path+f_ACAD_INVPROSA_INT_usr_rm # pankajaroa
    f_ACAD_full_USCAMHUM_usr_rm           = log_path+f_ACAD_INVPROSA_USCAMHCM_usr_rm # pankajaroa

    f_ACAD_full_license_rm                = log_path+f_ACAD_lincense_rm
    f_ACAD_full_INVPROSA_license_rm       = log_path+f_ACAD_INVPROSA_lincense_rm
    f_ACAD_full_Mechanicl_license_rm      = log_path+f_ACAD_Mechanicl_lincense_rm
    f_ACAD_full_Electrical_license_rm     = log_path+f_ACAD_Electrical_lincense_rm

    f_ACAD_full_INT_license_rm            = log_path+f_ACAD_INVENTOR_INT_lincense_rm # pankajaroa
    f_ACAD_full_USCAMHSM_license_rm       = log_path+f_ACAD_INVENTOR_USCAMHSM_lincense_rm # pankajaroa

    myfile_rm_autocad_1 = source_autocad+f_ACAD_usr_rm
    myfile_rm_autocad_2 = source_autocad+f_ACAD_INVPROSA_usr_rm
    myfile_rm_autocad_3 = source_autocad+f_ACAD_Mechanicl_usr_rm
    myfile_rm_autocad_4 = source_autocad+f_ACAD_Electrical_usr_rm

    myfile_rm_autocad_5 = source_autocad+f_ACAD_lincense_rm
    myfile_rm_autocad_6 = source_autocad+f_ACAD_INVPROSA_lincense_rm
    myfile_rm_autocad_7 = source_autocad+f_ACAD_Mechanicl_lincense_rm
    myfile_rm_autocad_8 = source_autocad+f_ACAD_Electrical_lincense_rm

    myfile_rm_autocad_9  = source_autocad+f_ACAD_INVPROSA_INT_usr_rm  # pankajaroa
    myfile_rm_autocad_10 = source_autocad+f_ACAD_INVPROSA_USCAMHCM_usr_rm # pankajaroa

    myfile_rm_autocad_11 = source_autocad+f_ACAD_INVENTOR_INT_lincense_rm # pankajaroa
    myfile_rm_autocad_12 = source_autocad+f_ACAD_INVENTOR_USCAMHSM_lincense_rm # pankajaroa

    p_rm_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_1,destination])
    sts_rm_1 = os.waitpid(p_rm_1.pid, 0)

    p_rm_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_2,destination])
    sts_rm_2 = os.waitpid(p_rm_2.pid, 0)

    p_rm_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_3,destination])
    sts_rm_3 = os.waitpid(p_rm_3.pid, 0)

    p_rm_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_4,destination])
    sts_rm_4 = os.waitpid(p_rm_4.pid, 0)

    p_rm_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_5,destination])
    sts_rm_5 = os.waitpid(p_rm_5.pid, 0)

    p_rm_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_6,destination])
    sts_rm_6 = os.waitpid(p_rm_6.pid, 0)

    p_rm_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_7,destination])
    sts_rm_7 = os.waitpid(p_rm_7.pid, 0)

    p_rm_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_8,destination])
    sts_rm_8 = os.waitpid(p_rm_8.pid, 0)


    p_rm_9 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_9,destination])
    sts_rm_9 = os.waitpid(p_rm_9.pid, 0)

    p_rm_10 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_10,destination])
    sts_rm_10 = os.waitpid(p_rm_10.pid, 0)

    p_rm_11 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_11,destination])
    sts_rm_11 = os.waitpid(p_rm_11.pid, 0)

    p_rm_12 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_autocad_12,destination])
    sts_rm_12 = os.waitpid(p_rm_12.pid, 0)

    # NX Previous day file transfer

    f_usr_NX_Assemblies_US_rm            = "US_Sites_rocnt67-NX_Assemblies-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_CheckMate_US_rm             = "US_Sites_rocnt67-Checkmate-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Drafting_US_rm              = "US_Sites_rocnt67-drafting-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_SolidModeling_US_rm         = "US_Sites_rocnt67-solid_modeling-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_US_rm                       = "US_Sites_rocnt67-NX-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Gateway_US_rm               = "US_Sites_rocnt67-gateway-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Machining_rm                = "NX_Machining_rocnt67-NX-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_ADVDES_US_rm                ="US_Sites_rocnt67-ADVDES-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  #Rajesh More 16 Jun                      
    f_usr_NX_Designer_US_rm              = "US_Sites_rocnt67-DESIGNER-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  #Rajesh More 16 Jun

    f_usr_NX_Assemblies_Global_rm        = "Global_rocnt423-NX_Assemblies-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_CheckMate_Global_rm         = "Global_rocnt423-Checkmate-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Drafting_Global_rm          = "Global_rocnt423-drafting-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_SolidModeling_Global_rm     = "Global_rocnt423-solid_modeling-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Global_rm                   = "Global_rocnt423-NX-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Gateway_Global_rm           = "Global_rocnt423-gateway-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Designer_Global_rm          = "Global_rocnt423-DESIGNER-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  #Rajesh More 16 June 2021
    f_usr_NX_AdvanceDesigner_Global_rm   = "Global_rocnt423-ADVDES-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  #Rajesh More 30 June 2021
    f_usr_NX_SC12500_US_rm               = "US_Sites_rocnt67-SC12500-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  #Rajesh More 30 June 2021
    f_usr_NX_SC12500_US_Global_rm        = "Global_rocnt423-SC12500-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  #Rajesh More 30 June 2021
    f_usr_NX_SC13500_US_rm               = "US_Sites_rocnt67-SC13500-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  #Rajesh More 30 June 2021
    f_usr_NX_SC13500_US_Global_rm        = "Global_rocnt423-SC13500-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_GMS4010_rm                  = "US_Sites_rocnt67-GMS4010-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_NX11100N_rm                 = "US_Sites_rocnt67-NX11100N-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_NX12100N_rm                 = "US_Sites_rocnt67-NX12100N-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_NS5010_Global_rm            = "Global_rocnt423-NS5010-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    # f_usr_NX_NS5010_US_rm                = "US_Sites_rocnt67-NS5010-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_NX_Sheet_Metal_Global_rm       = "Global_rocnt423-sheet_metal-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_PTC_US_rm                      = "US_Sites-PTC_US-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_PTC_Global_rm                  = "US_Sites-PTC_Global-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_PTC_Regional_rm                  = "US_Sites-PTC_Reginoal-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_usr_PTC_ToolDesign_rm                  = "US_Sites-PTC_ToolDesign-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"



    f_NX_full_usr_1_rm           =  log_path+f_usr_NX_Assemblies_US_rm
    f_NX_full_usr_2_rm           =  log_path+f_usr_NX_CheckMate_US_rm
    f_NX_full_usr_3_rm           =  log_path+f_usr_NX_Drafting_US_rm
    f_NX_full_usr_4_rm           =  log_path+f_usr_NX_SolidModeling_US_rm
    f_NX_full_usr_5_rm           =  log_path+f_usr_NX_US_rm
    f_NX_full_usr_6_rm           =  log_path+f_usr_NX_Gateway_US_rm
    f_NX_full_usr_7_rm           =  log_path+f_usr_NX_Machining_rm

    f_NX_full_usr_8_rm           =  log_path+f_usr_NX_Assemblies_Global_rm
    f_NX_full_usr_9_rm           =  log_path+f_usr_NX_CheckMate_Global_rm
    f_NX_full_usr_10_rm          =  log_path+f_usr_NX_Drafting_Global_rm
    f_NX_full_usr_11_rm          =  log_path+f_usr_NX_SolidModeling_Global_rm
    f_NX_full_usr_12_rm          =  log_path+f_usr_NX_Global_rm
    f_NX_full_usr_13_rm          =  log_path+f_usr_NX_Gateway_Global_rm
    f_NX_full_usr_14_rm          =  log_path+f_usr_NX_ADVDES_US_rm    #Rajesh More 16 June 2021
    f_NX_full_usr_15_rm          =  log_path+f_usr_NX_Designer_US_rm  #Rajesh More 16 June 2021
    f_NX_full_usr_16_rm          =  log_path+f_usr_NX_Designer_Global_rm  #Rajesh More 16 June 2021
    f_NX_full_usr_17_rm          =  log_path+f_usr_NX_AdvanceDesigner_Global_rm  #Rajesh More 30 June 2021
    f_NX_full_usr_18_rm          =  log_path+f_usr_NX_SC12500_US_rm
    f_NX_full_usr_19_rm          =  log_path+f_usr_NX_SC12500_US_Global_rm
    f_NX_full_usr_20_rm          =  log_path+f_usr_NX_SC13500_US_rm
    f_NX_full_usr_21_rm          =  log_path+f_usr_NX_SC13500_US_Global_rm
    f_NX_full_usr_22_rm          =  log_path+f_usr_NX_GMS4010_rm
    f_NX_full_usr_23_rm          =  log_path+f_usr_NX_NX11100N_rm
    f_NX_full_usr_24_rm          =  log_path+f_usr_NX_NX12100N_rm
    f_NX_full_usr_25_rm          =  log_path+f_usr_NX_NS5010_Global_rm
    # f_NX_full_usr_26_rm          =  log_path+f_usr_NX_NS5010_US_rm
    f_NX_full_usr_27_rm          =  log_path+f_usr_NX_Sheet_Metal_Global_rm
    f_PTC_US_full_usr_28_rm          =  log_path+f_usr_PTC_US_rm
    f_PTC_US_full_usr_29_rm          =  log_path+f_usr_PTC_Global_rm
    f_PTC_US_full_usr_30_rm          =  log_path+f_usr_PTC_Regional_rm
    f_PTC_US_full_usr_31_rm          =  log_path+f_usr_PTC_ToolDesign_rm




    file_1_rm = source_nx+f_usr_NX_Assemblies_US_rm
    file_2_rm = source_nx+f_usr_NX_CheckMate_US_rm
    file_3_rm = source_nx+f_usr_NX_Drafting_US_rm
    file_4_rm = source_nx+f_usr_NX_SolidModeling_US_rm
    file_5_rm = source_nx+f_usr_NX_US_rm
    file_6_rm = source_nx+f_usr_NX_Gateway_US_rm
    file_7_rm = source_nx+f_usr_NX_Machining_rm

    file_8_rm = source_nx+f_usr_NX_Assemblies_Global_rm
    file_9_rm = source_nx+f_usr_NX_CheckMate_Global_rm
    file_10_rm = source_nx+f_usr_NX_Drafting_Global_rm
    file_11_rm = source_nx+f_usr_NX_SolidModeling_Global_rm
    file_12_rm = source_nx+f_usr_NX_Global_rm
    file_13_rm = source_nx+f_usr_NX_Gateway_Global_rm
    file_14_rm = source_nx+f_usr_NX_ADVDES_US_rm  #Rajesh More 16 June 2021
    file_15_rm = source_nx+f_usr_NX_Designer_US_rm  #Rajesh More 16 June 2021
    file_16_rm = source_nx+f_usr_NX_Designer_Global_rm  #Rajesh More 16 June 2021
    file_17_rm = source_nx+f_usr_NX_AdvanceDesigner_Global_rm  #Rajesh More 30 June 2021 
    file_18_rm = source_nx+f_usr_NX_SC12500_US_rm
    file_19_rm = source_nx+f_usr_NX_SC12500_US_Global_rm
    file_20_rm = source_nx+f_usr_NX_SC13500_US_rm
    file_21_rm = source_nx+f_usr_NX_SC13500_US_Global_rm
    file_22_rm = source_nx+f_usr_NX_GMS4010
    file_23_rm = source_nx+f_usr_NX_NX11100N
    file_24_rm = source_nx+f_usr_NX_NX12100N
    file_25_rm = source_nx+f_usr_NX_NS5010_Global
    # file_26_rm = source_nx+f_usr_NX_NS5010_US
    file_27_rm = source_nx+f_usr_NX_Sheet_Metal_Global
    file_28_rm = source_nx+f_usr_PTC_US
    file_29_rm = source_nx+f_usr_PTC_Global
    file_30_rm = source_nx+f_usr_PTC_Regional
    file_31_rm = source_nx+f_usr_PTC_ToolDesign



        

    p_1_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_1_rm,destination])
    sts_1_rm = os.waitpid(p_1_rm.pid, 0)

    p_2_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_2_rm,destination])
    sts_2_rm = os.waitpid(p_2_rm.pid, 0)

    p_3_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_3_rm,destination])
    sts_3_rm = os.waitpid(p_3_rm.pid, 0)

    p_4_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_4_rm,destination])
    sts_4_rm = os.waitpid(p_4_rm.pid, 0)

    p_5_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_5_rm,destination])
    sts_5_rm = os.waitpid(p_5_rm.pid, 0)

    p_6_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_6_rm,destination])
    sts_6_rm = os.waitpid(p_6_rm.pid, 0)

    p_7_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_7_rm,destination])
    sts_7_rm = os.waitpid(p_7_rm.pid, 0)

    p_8_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_8_rm,destination])
    sts_8_rm = os.waitpid(p_8_rm.pid, 0)

    p_9_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_9_rm,destination])
    sts_9_rm = os.waitpid(p_9_rm.pid, 0)

    p_10_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_10_rm,destination])
    sts_10_rm = os.waitpid(p_10_rm.pid, 0)

    p_11_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_11_rm,destination])
    sts_11_rm = os.waitpid(p_11_rm.pid, 0)

    p_12_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_12_rm,destination])
    sts_12_rm = os.waitpid(p_12_rm.pid, 0)

    p_13_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_13_rm,destination])
    sts_13_rm = os.waitpid(p_13_rm.pid, 0)

    p_14_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_14_rm,destination])  # Rajesh More 16 Jun 2021
    sts_14_rm = os.waitpid(p_14_rm.pid, 0)                                                             # Rajesh More 16 Jun 2021

    p_15_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_15_rm,destination])   # Rajesh More 16 Jun 2021
    sts_14_rm = os.waitpid(p_15_rm.pid, 0)                                                              # Rajesh More 16 Jun 2021

    p_16_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_16_rm,destination])   # Rajesh More 16 Jun 2021
    sts_16_rm = os.waitpid(p_16_rm.pid, 0)                                                              # Rajesh More 16 Jun 2021

    p_17_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_17_rm,destination])   # Rajesh More 30 Jun 2021
    sts_17_rm = os.waitpid(p_17_rm.pid, 0)                                                              # Rajesh More 30 Jun 2021

    p_18_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_18_rm,destination])   
    sts_18_rm = os.waitpid(p_18_rm.pid, 0)   

    p_19_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_19_rm,destination])   
    sts_19_rm = os.waitpid(p_19_rm.pid, 0)  

    p_20_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_20_rm,destination])   
    sts_20_rm = os.waitpid(p_20_rm.pid, 0)   

    p_21_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_21_rm,destination])   
    sts_21_rm = os.waitpid(p_21_rm.pid, 0)   

    p_22_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_22_rm,destination])   
    sts_22_rm = os.waitpid(p_22_rm.pid, 0)   

    p_23_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_23_rm,destination])   
    sts_23_rm = os.waitpid(p_23_rm.pid, 0)   

    p_24_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_24_rm,destination])   
    sts_24_rm = os.waitpid(p_24_rm.pid, 0)   

    p_25_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_25_rm,destination])   
    sts_25_rm = os.waitpid(p_25_rm.pid, 0)   

#    p_26_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_26_rm,destination])   
#    sts_26_rm = os.waitpid(p_26_rm.pid, 0)   

    p_27_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_27_rm,destination])   
    sts_27_rm = os.waitpid(p_27_rm.pid, 0)   
    p_28_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_28_rm,destination])   
    sts_28_rm = os.waitpid(p_28_rm.pid, 0)
    p_29_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_29_rm,destination])   
    sts_29_rm = os.waitpid(p_29_rm.pid, 0)
    p_30_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_30_rm,destination])   
    sts_30_rm = os.waitpid(p_30_rm.pid, 0)
    p_31_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_31_rm,destination])   
    sts_31_rm = os.waitpid(p_31_rm.pid, 0)


    f_lic_NX_Assemblies_US_rm            = "US_Sites_rocnt67-NX_Assemblies-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_CheckMate_US_rm             = "US_Sites_rocnt67-Checkmate-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Drafting_US_rm              = "US_Sites_rocnt67-drafting-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_SolidModeling_US_rm         = "US_Sites_rocnt67-solid_modeling-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_US_rm                       = "US_Sites_rocnt67-NX-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Gateway_US_rm               = "US_Sites_rocnt67-gateway-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Machining_rm                = "NX_Machining_rocnt67-NX-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_ADVDES_US_rm                = "US_Sites_rocnt67-ADVDES-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt" # Rajesh More 16 June 2021
    f_lic_NX_Designer_US_rm              = "US_Sites_rocnt67-DESIGNER-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  # Rajesh More 16 June 2021


    f_lic_NX_Assemblies_Global_rm        = "Global_rocnt423-NX_Assemblies-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_CheckMate_Global_rm         = "Global_rocnt423-Checkmate-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Drafting_Global_rm          = "Global_rocnt423-drafting-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_SolidModeling_Global_rm     = "Global_rocnt423-solid_modeling-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Global_rm                   = "Global_rocnt423-NX-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Gateway_Global_rm           = "Global_rocnt423-gateway-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Designer_Global_rm          = "Global_rocnt423-DESIGNER-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  # Rajesh More 16 June 2021
    f_lic_NX_AdvanceDesigner_Global_rm   = "Global_rocnt423-ADVDES-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"  # Rajesh More 30 June 2021
    f_lic_NX_SC12500_US_rm               = "US_Sites_rocnt67-SC12500-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_SC12500_US_Global_rm        = "Global_rocnt423-SC12500-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_SC13500_US_rm               = "US_Sites_rocnt67-SC13500-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_SC13500_US_Global_rm        = "Global_rocnt423-SC13500-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_GMS4010_rm                  = "US_Sites_rocnt67-GMS4010-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_NX11100N_rm                 = "US_Sites_rocnt67-NX11100N-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_NX12100N_rm                 = "US_Sites_rocnt67-NX12100N-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_NS5010_Global_rm            = "Global_rocnt423-NS5010-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    # f_lic_NX_NS5010_US_rm                = "US_Sites_rocnt67-NS5010-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_NX_Sheet_Metal_Global_rm       = "Global_rocnt423-sheet_metal-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_PTC_US_rm                      = "US_Sites-PTC_US-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_PTC_Global_rm                      = "US_Sites-PTC_Global-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_PTC_Regional_rm                      = "US_Sites-PTC_Regional-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_lic_PTC_ToolDesign_rm                      = "US_Sites-PTC_ToolDesign-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"



    f_NX_full_lic_1_rm          =  log_path+f_lic_NX_Assemblies_US_rm
    f_NX_full_lic_2_rm          =  log_path+f_lic_NX_CheckMate_US_rm
    f_NX_full_lic_3_rm          =  log_path+f_lic_NX_Drafting_US_rm
    f_NX_full_lic_4_rm          =  log_path+f_lic_NX_SolidModeling_US_rm
    f_NX_full_lic_5_rm          =  log_path+f_lic_NX_US_rm
    f_NX_full_lic_6_rm          =  log_path+f_lic_NX_Gateway_US_rm
    f_NX_full_lic_7_rm          =  log_path+f_lic_NX_Machining_rm

    f_NX_full_lic_8_rm          =  log_path+f_lic_NX_Assemblies_Global_rm
    f_NX_full_lic_9_rm          =  log_path+f_lic_NX_CheckMate_Global_rm
    f_NX_full_lic_10_rm         =  log_path+f_lic_NX_Drafting_Global_rm
    f_NX_full_lic_11_rm         =  log_path+f_lic_NX_SolidModeling_Global_rm
    f_NX_full_lic_12_rm         =  log_path+f_lic_NX_Global_rm
    f_NX_full_lic_13_rm         =  log_path+f_lic_NX_Gateway_Global_rm
    f_NX_full_lic_14_rm         =  log_path+f_lic_NX_ADVDES_US_rm  # Rajesh More 16 June 2021
    f_NX_full_lic_15_rm         =  log_path+f_lic_NX_Designer_US_rm  # Rajesh More 16 June 2021
    f_NX_full_lic_16_rm         =  log_path+f_lic_NX_Designer_Global_rm  # Rajesh More 16 June 2021
    f_NX_full_lic_17_rm         =  log_path+f_lic_NX_AdvanceDesigner_Global_rm  # Rajesh More 30 June 2021
    f_NX_full_lic_18_rm         =  log_path+f_lic_NX_SC12500_US_rm
    f_NX_full_lic_19_rm         =  log_path+f_lic_NX_SC12500_US_Global_rm
    f_NX_full_lic_20_rm         =  log_path+f_lic_NX_SC13500_US_rm
    f_NX_full_lic_21_rm         =  log_path+f_lic_NX_SC13500_US_Global_rm
    f_NX_full_lic_22_rm         =  log_path+f_lic_NX_GMS4010_rm
    f_NX_full_lic_23_rm         =  log_path+f_lic_NX_NX11100N_rm
    f_NX_full_lic_24_rm         =  log_path+f_lic_NX_NX12100N_rm
    f_NX_full_lic_25_rm         =  log_path+f_lic_NX_NS5010_Global_rm
    # f_NX_full_lic_26_rm         =  log_path+f_lic_NX_NS5010_US_rm
    f_NX_full_lic_27_rm         =  log_path+f_lic_NX_Sheet_Metal_Global_rm
    f_PTC_US_full_lic_28_rm         =  log_path+f_lic_PTC_US_rm
    f_PTC_US_full_lic_29_rm         =  log_path+f_lic_PTC_Global_rm
    f_PTC_US_full_lic_30_rm         =  log_path+f_lic_PTC_Regional_rm
    f_PTC_US_full_lic_31_rm         =  log_path+f_lic_PTC_ToolDesign_rm





    file_1_lic_rm = source_nx+f_lic_NX_Assemblies_US_rm
    file_2_lic_rm = source_nx+f_lic_NX_CheckMate_US_rm
    file_3_lic_rm = source_nx+f_lic_NX_Drafting_US_rm
    file_4_lic_rm = source_nx+f_lic_NX_SolidModeling_US_rm
    file_5_lic_rm = source_nx+f_lic_NX_US_rm
    file_6_lic_rm = source_nx+f_lic_NX_Gateway_US_rm
    file_7_lic_rm = source_nx+f_lic_NX_Machining_rm

    file_8_lic_rm  = source_nx+f_lic_NX_Assemblies_Global_rm
    file_9_lic_rm  = source_nx+f_lic_NX_CheckMate_Global_rm
    file_10_lic_rm = source_nx+f_lic_NX_Drafting_Global_rm
    file_11_lic_rm = source_nx+f_lic_NX_SolidModeling_Global_rm
    file_12_lic_rm = source_nx+f_lic_NX_Global_rm
    file_13_lic_rm = source_nx+f_lic_NX_Gateway_Global_rm
    file_14_lic_rm = source_nx+f_lic_NX_ADVDES_US_rm  # Rajesh More 16 June 2021
    file_15_lic_rm = source_nx+f_lic_NX_Designer_US_rm  # Rajesh More 16 June 2021
    file_16_lic_rm = source_nx+f_lic_NX_Designer_Global_rm  # Rajesh More 16 June 2021
    file_17_lic_rm = source_nx+f_lic_NX_AdvanceDesigner_Global_rm  # Rajesh More 30 June 2021
    file_18_lic_rm = source_nx+f_lic_NX_SC12500_US_rm
    file_19_lic_rm = source_nx+f_lic_NX_SC12500_US_Global_rm
    file_20_lic_rm = source_nx+f_lic_NX_SC13500_US_rm
    file_21_lic_rm = source_nx+f_lic_NX_SC13500_US_Global_rm
    file_22_lic_rm = source_nx+f_lic_NX_GMS4010_rm
    file_23_lic_rm = source_nx+f_lic_NX_NX11100N_rm
    file_24_lic_rm = source_nx+f_lic_NX_NX12100N_rm
    file_25_lic_rm = source_nx+f_lic_NX_NS5010_Global_rm
    # file_26_lic_rm = source_nx+f_lic_NX_NS5010_US_rm
    file_27_lic_rm = source_nx+f_lic_NX_Sheet_Metal_Global_rm
    file_28_lic_rm = source_PTC+f_lic_PTC_US_rm
    file_29_lic_rm = source_PTC+f_lic_PTC_Global_rm
    file_30_lic_rm = source_PTC+f_lic_PTC_Regional_rm
    file_31_lic_rm = source_PTC+f_lic_PTC_ToolDesign_rm



    p_1_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_1_lic_rm,destination])
    sts_1_rm = os.waitpid(p_1_rm.pid, 0)

    p_2_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_2_lic_rm,destination])
    sts_2_rm = os.waitpid(p_2_rm.pid, 0)

    p_3_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_3_lic_rm,destination])
    sts_3_rm = os.waitpid(p_3_rm.pid, 0)

    p_4_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_4_lic_rm,destination])
    sts_4_rm = os.waitpid(p_4_rm.pid, 0)

    p_5_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_5_lic_rm,destination])
    sts_5_rm = os.waitpid(p_5_rm.pid, 0)

    p_6_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_6_lic_rm,destination])
    sts_6_rm = os.waitpid(p_6_rm.pid, 0)

    p_7_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_7_lic_rm,destination])
    sts_7_rm = os.waitpid(p_7_rm.pid, 0)

    p_8_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_8_lic_rm,destination])
    sts_8_rm = os.waitpid(p_8_rm.pid, 0)

    p_9_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_9_lic_rm,destination])
    sts_9_rm = os.waitpid(p_9_rm.pid, 0)

    p_10_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_10_lic_rm,destination])
    sts_10_rm = os.waitpid(p_10_rm.pid, 0)

    p_11_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_11_lic_rm,destination])
    sts_11_rm = os.waitpid(p_11_rm.pid, 0)

    p_12_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_12_lic_rm,destination])
    sts_12_rm = os.waitpid(p_12_rm.pid, 0)

    p_13_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_13_lic_rm,destination])
    sts_13_rm = os.waitpid(p_13_rm.pid, 0)

    p_14_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_14_lic_rm,destination])  # Rajesh More 16 Jun 2021
    sts_14_rm = os.waitpid(p_14_rm.pid, 0)                                                                 # Rajesh More 16 Jun 2021

    p_15_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_15_lic_rm,destination])  # Rajesh More 16 Jun 2021
    sts_15_rm = os.waitpid(p_15_rm.pid, 0)                                                                 # Rajesh More 16 Jun 2021

    p_16_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_16_lic_rm,destination])  # Rajesh More 16 Jun 2021
    sts_16_rm = os.waitpid(p_16_rm.pid, 0)                                                                 # Rajesh More 16 Jun 2021
    
    p_17_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_17_lic_rm,destination])  # Rajesh More 30 Jun 2021
    sts_17_rm = os.waitpid(p_17_rm.pid, 0)                                                                 # Rajesh More 30 Jun 2021

    p_18_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_18_lic_rm,destination])
    sts_18_rm = os.waitpid(p_18_rm.pid, 0)

    p_19_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_19_lic_rm,destination])
    sts_19_rm = os.waitpid(p_19_rm.pid, 0)

    p_20_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_20_lic_rm,destination])
    sts_20_rm = os.waitpid(p_20_rm.pid, 0)

    p_21_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_21_lic_rm,destination])
    sts_21_rm = os.waitpid(p_21_rm.pid, 0)

    p_22_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_22_lic_rm,destination])
    sts_22_rm = os.waitpid(p_22_rm.pid, 0)

    p_23_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_23_lic_rm,destination])
    sts_23_rm = os.waitpid(p_23_rm.pid, 0)

    p_24_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_24_lic_rm,destination])
    sts_24_rm = os.waitpid(p_24_rm.pid, 0)

    p_25_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_25_lic_rm,destination])
    sts_25_rm = os.waitpid(p_25_rm.pid, 0)

#    p_26_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_26_lic_rm,destination])
#    sts_26_rm = os.waitpid(p_26_rm.pid, 0)

    p_27_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_27_lic_rm,destination])
    sts_27_rm = os.waitpid(p_27_rm.pid, 0)

    p_28_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_28_lic_rm,destination])
    sts_28_rm = os.waitpid(p_28_rm.pid, 0)

    p_29_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_29_lic_rm,destination])
    sts_29_rm = os.waitpid(p_29_rm.pid, 0)

    p_30_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_30_lic_rm,destination])
    sts_30_rm = os.waitpid(p_30_rm.pid, 0)

    p_31_rm = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",file_31_lic_rm,destination])
    sts_31_rm = os.waitpid(p_31_rm.pid, 0)

    # Previous day file load for DFMPro
    f_DFMPro_usr_rm       = "Global_sites-DFMPro_8-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_DFMPro_lincense_rm  = "Global_sites-DFMPro_8-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

    f_DFMPro_full_usr_rm               = log_path+f_DFMPro_usr_rm
    f_DFMPro_full_license_rm           = log_path+f_DFMPro_lincense_rm

    myfile_rm_1 = source_dfmpro+f_DFMPro_usr_rm
    myfile_rm_2 = source_dfmpro+f_DFMPro_lincense_rm

    p_rm_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_1,destination])
    sts_rm_1 = os.waitpid(p_rm_1.pid, 0)

    p_rm_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_2,destination])
    sts_rm_2 = os.waitpid(p_rm_2.pid, 0)


###############################################

#user

    f_NX_AS5050_US_usr_rm                         = "US_Sites_rocnt67-AS5050-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_NS5010_Global_usr_rm                     = "Global_rocnt423-NS5010-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_UGID105_US_usr_rm                        = "US_Sites_rocnt67-UGID105-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_UGID100_US_usr_rm                        = "US_Sites_rocnt67-UGID100-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_US_usr_rm                  = "US_Sites_rocnt67-MFG-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_P1_US_usr_rm                  = "US_Sites_rocnt67-P1-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

#license

    f_NX_AS5050_US_license_rm                         = "US_Sites_rocnt67-AS5050-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_NS5010_Global_license_rm                     = "Global_rocnt423-NS5010-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_UGID105_US_license_rm                        = "US_Sites_rocnt67-UGID105-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_UGID100_US_license_rm                        = "US_Sites_rocnt67-UGID100-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_US_license_rm                  = "US_Sites_rocnt67-MFG-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_Manufacturing_P1_US_license_rm                  = "US_Sites_rocnt67-P1-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"


    myfile_NX_AS5050_US_usr_rm = source_nx+f_NX_AS5050_US_usr_rm
    myfile_NX_NS5010_Global_usr_rm = source_nx+f_NX_NS5010_Global_usr_rm
    myfile_NX_UGID105_US_usr_rm = source_nx+f_NX_UGID105_US_usr_rm
    myfile_NX_UGID100_US_usr_rm = source_nx+f_NX_UGID100_US_usr_rm
    myfile_NX_Manufacturing_US_usr_rm = source_nx+f_NX_Manufacturing_US_usr_rm
    myfile_NX_Manufacturing_P1_US_usr_rm = source_nx+f_NX_Manufacturing_P1_US_usr_rm
    myfile_NX_AS5050_US_license_rm = source_nx+f_NX_AS5050_US_license_rm
    myfile_NX_NS5010_Global_license_rm = source_nx+f_NX_NS5010_Global_license_rm
    myfile_NX_UGID105_US_license_rm = source_nx+f_NX_UGID105_US_license_rm
    myfile_NX_UGID100_US_license_rm = source_nx+f_NX_UGID100_US_license_rm
    myfile_NX_Manufacturing_US_license_rm = source_nx+f_NX_Manufacturing_US_license_rm
    myfile_NX_Manufacturing_P1_US_license_rm = source_nx+f_NX_Manufacturing_P1_US_license_rm


    myfile_NX_AS5050_US_usr_full_rm = log_path+f_NX_AS5050_US_usr_rm
    myfile_NX_NS5010_Global_usr_full_rm = log_path+f_NX_NS5010_Global_usr_rm
    myfile_NX_UGID105_US_usr_full_rm = log_path+f_NX_UGID105_US_usr_rm
    myfile_NX_UGID100_US_usr_full_rm = log_path+f_NX_UGID100_US_usr_rm
    myfile_NX_Manufacturing_US_usr_full_rm = log_path+f_NX_Manufacturing_US_usr_rm
    myfile_NX_Manufacturing_P1_US_usr_full_rm = log_path+f_NX_Manufacturing_P1_US_usr_rm
    myfile_NX_AS5050_US_license_full_rm = log_path+f_NX_AS5050_US_license_rm
    myfile_NX_NS5010_Global_license_full_rm = log_path+f_NX_NS5010_Global_license_rm
    myfile_NX_UGID105_US_license_full_rm = log_path+f_NX_UGID105_US_license_rm
    myfile_NX_UGID100_US_license_full_rm = log_path+f_NX_UGID100_US_license_rm
    myfile_NX_Manufacturing_US_license_full_rm = log_path+f_NX_Manufacturing_US_license_rm
    myfile_NX_Manufacturing_P1_US_license_full_rm = log_path+f_NX_Manufacturing_P1_US_license_rm


    p_1 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_AS5050_US_usr_rm,destination])
    sts_1 = os.waitpid(p_1.pid, 0)
    p_2 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_NS5010_Global_usr_rm,destination])
    sts_2 = os.waitpid(p_2.pid, 0)	
    p_3 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID105_US_usr_rm,destination])
    sts_3 = os.waitpid(p_3.pid, 0)	
    p_4 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID100_US_usr_rm,destination])
    sts_4 = os.waitpid(p_4.pid, 0)	
    p_5 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_US_usr_rm,destination])
    sts_5 = os.waitpid(p_5.pid, 0)	
    p_6 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_P1_US_usr_rm,destination])
    sts_6 = os.waitpid(p_6.pid, 0)	
    p_7 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_AS5050_US_license_rm,destination])
    sts_7 = os.waitpid(p_7.pid, 0)		
    p_8 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_NS5010_Global_license_rm,destination])
    sts_8 = os.waitpid(p_8.pid, 0)		
    p_9 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID105_US_license_rm,destination])
    sts_9 = os.waitpid(p_9.pid, 0)		
    p_10 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_UGID100_US_license_rm,destination])
    sts_10 = os.waitpid(p_10.pid, 0)
    p_11 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_US_license_rm,destination])
    sts_11 = os.waitpid(p_11.pid, 0)
    p_12 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_NX_Manufacturing_P1_US_license_rm,destination])
    sts_12 = os.waitpid(p_12.pid, 0)	


#user

    f_All_Autodesk_Products_usr_rm                  = "All-Autodesk_Apps-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_Autocad_Electrical_Mechanical_usr_rm          = "All-AutoCAD_Apps-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_Inventor_Inventor_Pro_usr_rm                  = "All-InventorPro_Apps-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"

#license

    f_All_Autodesk_Products_license_rm                  = "All-Autodesk_Apps-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_Autocad_Electrical_Mechanical_license_rm          = "All-AutoCAD_Apps-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_Inventor_Inventor_Pro_license_rm                  = "All-InventorPro_Apps-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"


    myfile_All_Autodesk_Products_usr_rm = source_autocad+f_All_Autodesk_Products_usr_rm
    myfile_Autocad_Electrical_Mechanical_usr_rm = source_autocad+f_Autocad_Electrical_Mechanical_usr_rm
    myfile_Inventor_Inventor_Pro_usr_rm = source_autocad+f_Inventor_Inventor_Pro_usr_rm
    myfile_All_Autodesk_Products_license_rm = source_autocad+f_All_Autodesk_Products_license_rm
    myfile_Autocad_Electrical_Mechanical_license_rm = source_autocad+f_Autocad_Electrical_Mechanical_license_rm
    myfile_Inventor_Inventor_Pro_license_rm = source_autocad+f_Inventor_Inventor_Pro_license_rm    


    myfile_All_Autodesk_Products_usr_full_rm = log_path+f_All_Autodesk_Products_usr_rm
    myfile_Autocad_Electrical_Mechanical_usr_full_rm = log_path+f_Autocad_Electrical_Mechanical_usr_rm
    myfile_Inventor_Inventor_Pro_usr_full_rm = log_path+f_Inventor_Inventor_Pro_usr_rm
    myfile_All_Autodesk_Products_license_full_rm = log_path+f_All_Autodesk_Products_license_rm
    myfile_Autocad_Electrical_Mechanical_license_full_rm = log_path+f_Autocad_Electrical_Mechanical_license_rm
    myfile_Inventor_Inventor_Pro_license_full_rm = log_path+f_Inventor_Inventor_Pro_license_rm    


    p_13 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_All_Autodesk_Products_usr_rm,destination])
    sts_13 = os.waitpid(p_13.pid, 0)	
    p_14 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Autocad_Electrical_Mechanical_usr_rm,destination])
    sts_14 = os.waitpid(p_14.pid, 0)	
    p_15 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Inventor_Inventor_Pro_usr_rm,destination])
    sts_15 = os.waitpid(p_15.pid, 0)
    p_16 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_All_Autodesk_Products_license_rm,destination])
    sts_16 = os.waitpid(p_16.pid, 0)	
    p_17 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Autocad_Electrical_Mechanical_license_rm,destination])
    sts_17 = os.waitpid(p_17.pid, 0)
    p_18 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_Inventor_Inventor_Pro_license_rm,destination])
    sts_18 = os.waitpid(p_18.pid, 0)	
###########################################################
# Code by SM
    f_NX_usr_rm       = "PBO-NX93100-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_NX_license_rm       = "PBO-NX93100-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    
    f_NX_full_usr_19_rm  = log_path+f_NX_usr_rm
    f_NX_full_license_20_rm = log_path+f_NX_license_rm
	
    myfile_rm_19 = source_nx + f_NX_usr_rm
    myfile_rm_20 = source_nx + f_NX_license_rm
	
	
    p_rm_19 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_19,destination])
    sts_rm_19 = os.waitpid(p_rm_19.pid, 0)
    
    p_rm_20 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_20,destination])
    sts_rm_20 = os.waitpid(p_rm_20.pid, 0)
    
    #Catia Zone wise Report
    
    f_Catia_Zone_wise_Report_usr_rm       = "Europe_Sites-CATIA_V5-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_Catia_Zone_wise_Report_license_rm   = "Europe_Sites-CATIA_V5-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    
    f_Catia_Zone_wise_Report_full_usr_21_rm  = log_path+f_Catia_Zone_wise_Report_usr_rm
    f_Catia_Zone_wise_Report_full_license_22_rm = log_path+f_Catia_Zone_wise_Report_license_rm
	
    myfile_rm_21 = source_Catia_Zone_wise_Report + f_Catia_Zone_wise_Report_usr_rm
    myfile_rm_22 = source_Catia_Zone_wise_Report + f_Catia_Zone_wise_Report_license_rm
	
	
    p_rm_21 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_21,destination])
    sts_rm_21 = os.waitpid(p_rm_21.pid, 0)
    
    p_rm_22 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_22,destination])
    sts_rm_22 = os.waitpid(p_rm_22.pid, 0)
    
    #Germany
    
    f_Germany_usr_rm       = "Germany_Sites-CATIA_V5-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_Germany_license_rm       = "Germany_Sites-CATIA_V5-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    
    f_Germany_full_usr_23_rm  = log_path+f_Germany_usr_rm
    f_Germany_full_license_24_rm = log_path+f_Germany_license_rm
	
    myfile_rm_23 = source_Germany + f_Germany_usr_rm
    myfile_rm_24 = source_Germany + f_Germany_license_rm
	
	
    p_rm_23 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_23,destination])
    sts_rm_23 = os.waitpid(p_rm_23.pid, 0)
    
    p_rm_24 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_24,destination])
    sts_rm_24 = os.waitpid(p_rm_24.pid, 0)
    
	#PBO	
    f_PBO_usr_rm       = "PBO_Sites-CATIA_V5-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_PBO_license_rm       = "PBO_Sites-CATIA_V5-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    
    f_PBO_full_usr_25_rm  = log_path+f_PBO_usr_rm
    f_PBO_full_license_26_rm = log_path+f_PBO_license_rm
	
    myfile_rm_25 = source_PBO + f_PBO_usr_rm
    myfile_rm_26 = source_PBO + f_PBO_license_rm
	
	
    p_rm_25 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_25,destination])
    sts_rm_25 = os.waitpid(p_rm_25.pid, 0)
    
    p_rm_26= subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_26,destination])
    sts_rm_26 = os.waitpid(p_rm_26.pid, 0)
	
    
    #US1
    f_US1_usr_rm       = "US1_Sites-CATIA_V5-users-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    f_US1_license_rm       = "US1_Sites-CATIA_V5-licenses-"+prev_date_year_STR+"-"+prev_date_Day_of_the_Year_STR+".txt"
    
    f_US1_full_usr_27_rm  = log_path+f_US1_usr_rm
    f_US1_full_license_28_rm = log_path+f_US1_license_rm
	
    myfile_rm_27 = source_US1 + f_US1_usr_rm
    myfile_rm_28 = source_US1 + f_US1_license_rm
	
	
    p_rm_27 = subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_27,destination])
    sts_rm_27 = os.waitpid(p_rm_27.pid, 0)
    
    p_rm_28= subprocess.Popen(["sudo","scp","-i","/home/cadrpt/.ssh/id_rsa",myfile_rm_26,destination])
    sts_rm_28 = os.waitpid(p_rm_28.pid, 0)

#End
###############################################


    # Defining target DB connection
    # tns_dsn = cx_Oracle.makedsn('172.31.53.12','1521','BIDWDEV') # this is for Dev credientels
#    tns_dsn = cx_Oracle.makedsn('172.28.87.15','1525','BIDWPRD')
    tns_dsn = cx_Oracle.makedsn(cdtls.oracle_bidwprd.host, cdtls.oracle_bidwprd.port, service_name=cdtls.oracle_bidwprd.service_name) 
#    con_ORACLE = cx_Oracle.connect('AAM','hdquowel',dsn=tns_dsn)
    con_ORACLE = cx_Oracle.connect(user=cdtls.oracle_bidwprd.user, password=cdtls.oracle_bidwprd.password, dsn=tns_dsn) 

    #con_ORACLE = cx_Oracle.connect("PROD_AAM_RO,prod_aam_ro@aamlxbidbp001.aam.net:1525/BIDWPRD")

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
        print ("try: ")
        print ("Check 1")
    # Inserting data into user staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into User Staging Table')
####################################################################################################
        if os.path.isfile(f_PTC_full_usr) and os.path.getsize(f_PTC_full_usr) > 0:
            user_type  =  'PTC Creo'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
               # sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.1")
        if os.path.isfile(f_PTC_full_usr_mathcad) and os.path.getsize(f_PTC_full_usr_mathcad) > 0:
            user_type  =  'PTC Mathcad'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr_mathcad, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
               # sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_mathcad+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_mathcad+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.2")
        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

    # Inserting users data of previous day into staging tables
####################################################################################################
        Logger.start(log_info = 'Inserting Users Data Of Previous Day Into Staging Tables')
####################################################################################################
        if os.path.isfile(f_PTC_full_usr_rm) and os.path.getsize(f_PTC_full_usr_rm) > 0:
            user_type  =  'PTC Creo'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.3")
        if os.path.isfile(f_PTC_full_usr_mathcad_rm) and os.path.getsize(f_PTC_full_usr_mathcad_rm) > 0:
            user_type  =  'PTC Mathcad'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr_mathcad_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_mathcad_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_mathcad_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.4")
        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

    # Inserting data into License staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into License Staging Table')
####################################################################################################
        if os.path.isfile(f_PTC_full_license) and os.path.getsize(f_PTC_full_license) > 0:
            license_type  =  'PTC Creo'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.5")
        if os.path.isfile(f_PTC_full_license_mathcad) and os.path.getsize(f_PTC_full_license_mathcad) > 0:
            license_type  =  'PTC Mathcad'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license_mathcad,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_mathcad+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_mathcad+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.6")
        if os.path.isfile(f_PTC_full_license_rm) and os.path.getsize(f_PTC_full_license_rm) > 0:
            license_type  =  'PTC Creo'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.7")
        if os.path.isfile(f_PTC_full_license_mathcad_rm) and os.path.getsize(f_PTC_full_license_mathcad_rm) > 0:
            license_type  =  'PTC Mathcad'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license_mathcad_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_mathcad_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_mathcad_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.7")
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)

    # Inserting data into user staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into User Staging Table')
####################################################################################################
        if os.path.isfile(f_PTC_full_usr_1) and os.path.getsize(f_PTC_full_usr_1) > 0:
            user_type  =  'PTC MetalDyne'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr_1, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.8")
        if os.path.isfile(f_PTC_full_usr_2) and os.path.getsize(f_PTC_full_usr_2) > 0:
            user_type  =  'PTC MetalDyne MoldDesign'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr_2, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_2+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_2+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.9")
        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

    # Inserting users data of previous day into staging tables
####################################################################################################
        Logger.start(log_info = 'Inserting Users Data Of Previous Day Into Staging Tables')
####################################################################################################
        if os.path.isfile(f_PTC_full_usr_1_rm) and os.path.getsize(f_PTC_full_usr_1_rm) > 0:
            user_type  =  'PTC MetalDyne'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr_1_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.10")
        if os.path.isfile(f_PTC_full_usr_2_rm) and os.path.getsize(f_PTC_full_usr_2_rm) > 0:
            user_type  =  'PTC MetalDyne MoldDesign'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_usr_2_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_2_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_2_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.11")
        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))

    # Inserting data into License staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into License Staging Table')
####################################################################################################
        if os.path.isfile(f_PTC_full_license_1) and os.path.getsize(f_PTC_full_license_1) > 0:
            license_type  =  'PTC MetalDyne'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license_1,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_1+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_1+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.12")
        if os.path.isfile(f_PTC_full_license_2) and os.path.getsize(f_PTC_full_license_2) > 0:
            license_type  =  'PTC MetalDyne MoldDesign'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license_2,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_2+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_2+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.13")
        if os.path.isfile(f_PTC_full_license_1_rm) and os.path.getsize(f_PTC_full_license_1_rm) > 0:
            license_type  =  'PTC MetalDyne'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license_1_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_1_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_1_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.14")
        if os.path.isfile(f_PTC_full_license_2_rm) and os.path.getsize(f_PTC_full_license_2_rm) > 0:
            license_type  =  'PTC MetalDyne MoldDesign'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_full_license_2_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_PTC_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_2_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PTC_lincense_2_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.15")
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))

        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
     
        print (f_CATIA_full_usr_US)
        print ("1.16")
#        if os.path.isfile(f_CATIA_full_usr_US) and os.path.getsize(f_CATIA_full_usr_US) > 0:
#            user_type  =  'US'
#            app_type   =  'CAD'
#            app_name   =  'CATIA'
#            data = pd.read_csv(f_CATIA_full_usr_US, header=None)
#            for index,row in data.iterrows():
#                user_name = row[0] ##date
#                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_CATIA_usr_US+"','"+str(app_type)+"','"+str(app_name)+"')"
#                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 1.17")
        if os.path.isfile(f_CATIA_full_usr_NonUS) and os.path.getsize(f_CATIA_full_usr_NonUS) > 0:
            user_type  =  'China'
            app_type   =  'CAD'
            app_name   =  'CATIA'
            data = pd.read_csv(f_CATIA_full_usr_NonUS, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_CATIA_usr_NonUS+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)
        print ("Check 2")
        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        
#        if os.path.isfile(f_CATIA_full_usr_US_rm) and os.path.getsize(f_CATIA_full_usr_US_rm) > 0:
#            user_type  =  'US'
#            app_type   =  'CAD'
#            app_name   =  'CATIA'
#            data = pd.read_csv(f_CATIA_full_usr_US_rm , header=None)
#            for index,row in data.iterrows():
#                user_name = row[0] ##date
#                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_CATIA_usr_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
#                #print(sql)
#                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_CATIA_full_usr_NonUS_rm) and os.path.getsize(f_CATIA_full_usr_NonUS_rm) > 0:
            user_type  =  'China'
            app_type   =  'CAD'
            app_name   =  'CATIA'
            data = pd.read_csv(f_CATIA_full_usr_NonUS_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_CATIA_usr_NonUS_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))

        if os.path.isfile(f_CATIA_full_license_US) and os.path.getsize(f_CATIA_full_license_US) > 0:
            license_type  =  'US'
            app_type   =  'CAD'
            app_name   =  'CATIA'
            data = pd.read_csv(f_CATIA_full_license_US,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_CATIA_lincense_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_CATIA_full_license_NonUS) and os.path.getsize(f_CATIA_full_license_NonUS) > 0:
            license_type  =  'China'
            app_type   =  'CAD'
            app_name   =  'CATIA'
            data = pd.read_csv(f_CATIA_full_license_NonUS,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_CATIA_lincense_NonUS+"','"+str(app_type)+"','"+str(app_name)+"')" 
                
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_CATIA_full_license_US_rm)) and (os.stat(f_CATIA_full_license_US_rm).st_size != 0)):
            license_type  =  'US'
            app_type   =  'CAD'
            app_name   =  'CATIA'
            data = pd.read_csv(f_CATIA_full_license_US_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_CATIA_lincense_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_CATIA_full_license_NonUS_rm)) and (os.stat(f_CATIA_full_license_NonUS_rm).st_size != 0)):
            license_type  =  'China'
            app_type   =  'CAD'
            app_name   =  'CATIA'
            data = pd.read_csv(f_CATIA_full_license_NonUS_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_CATIA_lincense_NonUS_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
            
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)

        if os.path.isfile(f_SOLIDWORKS_full_usr) and os.path.getsize(f_SOLIDWORKS_full_usr) > 0:
            user_type  =  'SolidWorks Users'
            app_type   =  'CAD'
            app_name   =  'SolidWorks'
            data = pd.read_csv(f_SOLIDWORKS_full_usr, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
            #sql = "insert into AAM_SOLIDWORKS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDWORKS_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDWORKS_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

        if os.path.isfile(f_SOLIDWORKS_full_usr_rm) and os.path.getsize(f_SOLIDWORKS_full_usr_rm) > 0:
            user_type  =  'SolidWorks Users'
            app_type   =  'CAD'
            app_name   =  'SolidWorks'
            data = pd.read_csv(f_SOLIDWORKS_full_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
        #sql = "insert into AAM_SOLIDWORKS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDWORKS_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDWORKS_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))

        if os.path.isfile(f_SOLIDWORKS_full_license) and os.path.getsize(f_SOLIDWORKS_full_license) > 0:
            license_type  =  'SolidWorks license'
            app_type   =  'CAD'
            app_name   =  'SolidWorks'
            data = pd.read_csv(f_SOLIDWORKS_full_license,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_SOLIDWORKS_full_license_rm)) and (os.stat(f_SOLIDWORKS_full_license_rm).st_size != 0)):
            license_type  =  'SolidWorks license'
            app_type   =  'CAD'
            app_name   =  'SolidWorks'
            data = pd.read_csv(f_SOLIDWORKS_full_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
             #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
        print ("Check 3")    
        if os.path.isfile(f_SOLIDEDGE_full_usr) and os.path.getsize(f_SOLIDEDGE_full_usr) > 0:
            user_type  =  'SolidEdge Users'
            app_type   =  'CAD'
            app_name   =  'SolidEdge'
            data = pd.read_csv(f_SOLIDEDGE_full_usr, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
       #sql = "insert into AAM_SOLIDWORKS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDWORKS_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDEDGE_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

        if os.path.isfile(f_SOLIDEDGE_full_usr_rm) and os.path.getsize(f_SOLIDEDGE_full_usr_rm) > 0:
            user_type  =  'SolidEdge Users'
            app_type   =  'CAD'
            app_name   =  'SolidEdge'
            data = pd.read_csv(f_SOLIDEDGE_full_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
        #sql = "insert into AAM_SOLIDWORKS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDWORKS_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_SOLIDEDGE_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))

        if os.path.isfile(f_SOLIDEDGE_full_license) and os.path.getsize(f_SOLIDEDGE_full_license) > 0:
            license_type  =  'SolidEdge license'
            app_type   =  'CAD'
            app_name   =  'SolidEdge'
            data = pd.read_csv(f_SOLIDEDGE_full_license,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDEDGE_lincense+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_SOLIDEDGE_full_license_rm)) and (os.stat(f_SOLIDEDGE_full_license_rm).st_size != 0)):
            license_type  =  'SolidEdge license'
            app_type   =  'CAD'
            app_name   =  'SolidEdge'
            data = pd.read_csv(f_SOLIDEDGE_full_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                    #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDEDGE_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
            

        if os.path.isfile(f_ACAD_full_usr) and os.path.getsize(f_ACAD_full_usr) > 0:
            user_type  =  'Autocad'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_usr, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_INVPROSA_usr) and os.path.getsize(f_ACAD_full_INVPROSA_usr) > 0:
            user_type  =  'Inventor US'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_INVPROSA_usr , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
             #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_Mechanicl_usr) and os.path.getsize(f_ACAD_full_Mechanicl_usr) > 0:
            user_type  =  'Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_Mechanicl_usr ,header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
             #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Mechanicl_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Mechanicl_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_Electrical_usr) and os.path.getsize(f_ACAD_full_Electrical_usr) > 0:
            user_type  =  'Electrical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_Electrical_usr , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
             #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Electrical_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Electrical_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_INT_usr) and os.path.getsize(f_ACAD_full_INT_usr) > 0:
            user_type  =  'Inventor NonUS'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_INT_usr , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
          #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_INT_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_INT_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_USCAMHUM_usr) and os.path.getsize(f_ACAD_full_USCAMHUM_usr) > 0:
            user_type  =  'CAMHSM'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_USCAMHUM_usr , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_USCAMHCM_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_USCAMHCM_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql) 

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

        if os.path.isfile(f_ACAD_full_usr_rm) and os.path.getsize(f_ACAD_full_usr_rm) > 0:
            user_type  =  'Autocad'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_INVPROSA_usr_rm) and os.path.getsize(f_ACAD_full_INVPROSA_usr_rm) > 0:
            user_type  =  'Inventor US'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_INVPROSA_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
            #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_Mechanicl_usr_rm) and os.path.getsize(f_ACAD_full_Mechanicl_usr_rm) > 0:
            user_type  =  'Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_Mechanicl_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
          #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Mechanicl_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Mechanicl_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_Electrical_usr_rm) and os.path.getsize(f_ACAD_full_Electrical_usr_rm) > 0:
            user_type  =  'Electrical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_Electrical_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Electrical_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_Electrical_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_INT_usr_rm) and os.path.getsize(f_ACAD_full_INT_usr_rm) > 0:
            user_type  =  'Inventor NonUS'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_INT_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_INT_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_INT_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_USCAMHUM_usr_rm) and os.path.getsize(f_ACAD_full_USCAMHUM_usr_rm) > 0:
            user_type  =  'CAMHSM'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_USCAMHUM_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_AUTOCAD_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_USCAMHCM_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_ACAD_INVPROSA_USCAMHCM_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        #cs_ORACLE.execute(MERGE_AAM_AUTOCAD_USER_DETAILS.format(prev_day_date))
        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

        if os.path.isfile(f_ACAD_full_license) and os.path.getsize(f_ACAD_full_license) > 0:
            license_type  =  'Autocad'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_license,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_lincense+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_INVPROSA_license) and os.path.getsize(f_ACAD_full_INVPROSA_license) > 0:
            license_type  =  'Inventor US'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data3 = pd.read_csv(f_ACAD_full_INVPROSA_license,sep=' ')
            for index3,row3 in data3.iterrows():
                date = row3[0] ##date
                license_used = row3[1]
                license_total = row3[2]
                #sql3 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date3)+","+str(license_used3)+","+str(license_total3)+",'"+license_type3+"','"+f_ACAD_INVPROSA_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVPROSA_lincense+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_Mechanicl_license) and os.path.getsize(f_ACAD_full_Mechanicl_license) > 0:   
            license_type  =  'Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data1 = pd.read_csv(f_ACAD_full_Mechanicl_license,sep=' ')
            for index1,row1 in data1.iterrows():
                date = row1[0] ##date
                license_used = row1[1]
                license_total = row1[2]
                #sql1 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date1)+","+str(license_used1)+","+str(license_total1)+",'"+license_type1+"','"+f_ACAD_Mechanicl_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_Mechanicl_lincense+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_Electrical_license) and os.path.getsize(f_ACAD_full_Electrical_license) > 0:
            license_type  =  'Electrical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data2 = pd.read_csv(f_ACAD_full_Electrical_license,sep=' ')
            for index2,row2 in data2.iterrows():
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_Electrical_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_Electrical_lincense+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_INT_license) and os.path.getsize(f_ACAD_full_INT_license) > 0:
            license_type  =  'Inventor NonUS'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data2 = pd.read_csv(f_ACAD_full_INT_license,sep=' ')
            for index2,row2 in data2.iterrows():
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_INVENTOR_INT_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_ACAD_full_USCAMHSM_license) and os.path.getsize(f_ACAD_full_USCAMHSM_license) > 0:
            license_type  =  'CAMHSM'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data2 = pd.read_csv(f_ACAD_full_USCAMHSM_license,sep=' ')
            for index2,row2 in data2.iterrows():
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_INVENTOR_USCAMHSM_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_USCAMHSM_lincense+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

    # Loading data from License files from previous day

        if  ((path.exists(f_ACAD_full_license_rm)) and (os.stat(f_ACAD_full_license_rm).st_size != 0)):
            license_type  =  'Autocad'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_ACAD_full_INVPROSA_license_rm)) and (os.stat(f_ACAD_full_INVPROSA_license_rm).st_size != 0)):
            license_type  =  'Inventor US'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_INVPROSA_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVPROSA_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVPROSA_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_ACAD_full_Mechanicl_license_rm)) and (os.stat(f_ACAD_full_Mechanicl_license_rm).st_size != 0)):
            license_type  =  'Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_Mechanicl_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_Mechanicl_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_Mechanicl_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_ACAD_full_Electrical_license_rm)) and (os.stat(f_ACAD_full_Electrical_license_rm).st_size != 0)):
            license_type  =  'Electrical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_Electrical_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_Electrical_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_Electrical_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_ACAD_full_INT_license_rm)) and (os.stat(f_ACAD_full_INT_license_rm).st_size != 0)):
            license_type  =  'Inventor NonUS'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_INT_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_ACAD_full_USCAMHSM_license_rm)) and (os.stat(f_ACAD_full_USCAMHSM_license_rm).st_size != 0)):
            license_type  =  'CAMHSM'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(f_ACAD_full_USCAMHSM_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_USCAMHSM_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_USCAMHSM_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        #cs_ORACLE.execute(MERGE_AAM_AUTOCAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)


        if os.path.isfile(f_NX_full_usr_1) and os.path.getsize(f_NX_full_usr_1) > 0:
            user_type  =  'NX Assemblies US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_1, header=None)
            for index,row in data.iterrows():
                user_name = row[0]
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Assemblies_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Assemblies_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_2) and os.path.getsize(f_NX_full_usr_2) > 0:
            user_type  =  'NX CheckMate US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_2, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_CheckMate_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_CheckMate_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_3) and os.path.getsize(f_NX_full_usr_3) > 0:
            user_type  =  'NX Drafting US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_3, header=None)
            for index,row in data.iterrows():
                user_name = row[0]
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Drafting_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Drafting_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_4) and os.path.getsize(f_NX_full_usr_4) > 0:
            user_type  =  'NX SolidModeling US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_4, header=None)
            for index,row in data.iterrows():
                user_name = row[0]
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SolidModeling_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SolidModeling_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_5) and os.path.getsize(f_NX_full_usr_5) > 0:
            user_type  =  'NX US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_5, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_6) and os.path.getsize(f_NX_full_usr_6) > 0:
            user_type  =  'NX Gateway US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_6, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_7) and os.path.getsize(f_NX_full_usr_7) > 0:
            user_type  =  'NX-Machining'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_7, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NXE_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Machining+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Machining+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_usr_8) and os.path.getsize(f_NX_full_usr_8) > 0:
            user_type  =  'NX Assemblies Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_8, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Assemblies_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Assemblies_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        if os.path.isfile(f_NX_full_usr_9) and os.path.getsize(f_NX_full_usr_9) > 0:
            user_type  =  'NX CheckMate Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_9, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_CheckMate_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_CheckMate_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_10) and os.path.getsize(f_NX_full_usr_10) > 0:
            user_type  =  'NX Drafting Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_10, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Drafting_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Drafting_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_11) and os.path.getsize(f_NX_full_usr_11) > 0:
            user_type  =  'NX SolidModeling Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_11, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SolidModeling_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SolidModeling_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_12) and os.path.getsize(f_NX_full_usr_12) > 0:
            user_type  =  'NX Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_12, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_13) and os.path.getsize(f_NX_full_usr_13) > 0:
            user_type  =  'NX Gateway Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_13, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 
##################################### Added By Rajesh More 16 Jun 2021##################################################################################################################
        print("***************************************************************************************************************************************************")        
        if os.path.isfile(f_NX_full_usr_14) and os.path.getsize(f_NX_full_usr_14) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-AdvanceDesigner -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_14, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"               
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_ADVDES_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        print('2222222222222222222222222222222')
        if os.path.isfile(f_NX_full_usr_15) and os.path.getsize(f_NX_full_usr_15) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-Designer -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_15, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Designer_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        print('22222222222222222AAAAAAAAAAAAAAAAAA')                
        if os.path.isfile(f_NX_full_usr_16) and os.path.getsize(f_NX_full_usr_16) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-Designer -Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_16, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Designer_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)                

        if os.path.isfile(f_NX_full_usr_17) and os.path.getsize(f_NX_full_usr_17) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-AdvanceDesigner-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_17, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_AdvanceDesigner_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)      
        
        if os.path.isfile(f_NX_full_usr_18) and os.path.getsize(f_NX_full_usr_18) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-SC12500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_18, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC12500_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)   
        
        if os.path.isfile(f_NX_full_usr_19) and os.path.getsize(f_NX_full_usr_19) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-SC12500-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_19, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC12500_US_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)   
        
        if os.path.isfile(f_NX_full_usr_20) and os.path.getsize(f_NX_full_usr_20) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-SC13500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_20, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC13500_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)    
        
        if os.path.isfile(f_NX_full_usr_21) and os.path.getsize(f_NX_full_usr_21) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-SC13500-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_21, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC13500_US_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)    


        if os.path.isfile(f_NX_full_usr_22) and os.path.getsize(f_NX_full_usr_22) > 0:    # Rajesh More 16 June 2021
            user_type  =  'NX-GMS4010'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_22, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_GMS4010+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)    

        if os.path.isfile(f_NX_full_usr_23) and os.path.getsize(f_NX_full_usr_23) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'NX-NX11100N'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_usr_23, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NX11100N+"','"+str(app_type)+"','"+str(app_name)+"')"
                        INSERT_TABLE = cs_ORACLE.execute(sql)    

        if os.path.isfile(f_NX_full_usr_24) and os.path.getsize(f_NX_full_usr_24) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'NX-NX12100N'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_usr_24, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NX12100N+"','"+str(app_type)+"','"+str(app_name)+"')"
                        INSERT_TABLE = cs_ORACLE.execute(sql)    


        if os.path.isfile(f_NX_full_usr_25) and os.path.getsize(f_NX_full_usr_25) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'NX-NS5010-Global'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_usr_25, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NS5010_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                        INSERT_TABLE = cs_ORACLE.execute(sql) 

        # if os.path.isfile(f_NX_full_usr_26) and os.path.getsize(f_NX_full_usr_26) > 0:    # Rajesh More 16 June 2021
        #             user_type  =  'NX-NS5010-US'
        #             app_type   =  'CAD'
        #             app_name   =  'NX'
        #             data = pd.read_csv(f_NX_full_usr_26, header=None)
        #             for index,row in data.iterrows():
        #                 user_name = row[0] ##date
        #                 #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
        #                 sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NS5010_US+"','"+str(app_type)+"','"+str(app_name)+"')"
        #                 INSERT_TABLE = cs_ORACLE.execute(sql) 

        if os.path.isfile(f_NX_full_usr_27) and os.path.getsize(f_NX_full_usr_27) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'NX-Sheet_Metal-Global'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_usr_27, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Sheet_Metal_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                        INSERT_TABLE = cs_ORACLE.execute(sql)      

        if os.path.isfile(f_PTC_full_usr_28) and os.path.getsize(f_PTC_full_usr_28) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'PTC'
                    app_type   =  'CAD'
                    app_name   =  'PTC US'
                    data = pd.read_csv(f_PTC_full_usr_28, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_US+"','"+str(app_type)+"','"+str(app_name)+"')"
                        INSERT_TABLE = cs_ORACLE.execute(sql)                                               

        if os.path.isfile(f_PTC_full_usr_29) and os.path.getsize(f_PTC_full_usr_29) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'PTC'
                    app_type   =  'CAD'
                    app_name   =  'PTC Global'
                    data = pd.read_csv(f_PTC_full_usr_29, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_Global+"','"+str(app_type)+"','"+str(app_name)+"')"
                        INSERT_TABLE = cs_ORACLE.execute(sql)  

        if os.path.isfile(f_PTC_full_usr_30) and os.path.getsize(f_PTC_full_usr_30) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'PTC'
                    app_type   =  'CAD'
                    app_name   =  'PTC Regional'
                    data = pd.read_csv(f_PTC_full_usr_30, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_Regional+"','"+str(app_type)+"','"+str(app_name)+"')"
                        INSERT_TABLE = cs_ORACLE.execute(sql)  

        if os.path.isfile(f_PTC_full_usr_31) and os.path.getsize(f_PTC_full_usr_31) > 0:    # Rajesh More 16 June 2021
                    user_type  =  'PTC'
                    app_type   =  'CAD'
                    app_name   =  'PTC ToolDesign'
                    data = pd.read_csv(f_PTC_full_usr_31, header=None)
                    for index,row in data.iterrows():
                        user_name = row[0] ##date
                        #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_ToolDesign+"','"+str(app_type)+"','"+str(app_name)+"')"
                        print('PTC ToolDesign',sql)
                        INSERT_TABLE = cs_ORACLE.execute(sql)  
######################################Portion above this line is edited by Rajesh More on 17 Jun 2021################################################################

 
        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        
        
        print('3333333333333333333333333333333')        
        if os.path.isfile(f_NX_full_usr_1_rm) and os.path.getsize(f_NX_full_usr_1_rm) > 0:
            user_type  =  'NX Assemblies US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_1_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Assemblies_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+str(f_usr_NX_Assemblies_US_rm)+"','"+str(app_type)+"','"+str(app_name)+"')"
                print('sql NX Assemblies US',sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_usr_2_rm) and os.path.getsize(f_NX_full_usr_2_rm) > 0:
            user_type  =  'NX CheckMate US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_2_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_CheckMate_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+str(f_usr_NX_CheckMate_US_rm)+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_3_rm) and os.path.getsize(f_NX_full_usr_3_rm) > 0:
            user_type  =  'NX Drafting US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_3_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Drafting_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+str(f_usr_NX_Drafting_US_rm)+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_4_rm) and os.path.getsize(f_NX_full_usr_4_rm) > 0:
            user_type  =  'NX SolidModeling US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_4_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SolidModeling_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+str(f_usr_NX_SolidModeling_US_rm)+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_5_rm) and os.path.getsize(f_NX_full_usr_5_rm) > 0:
            user_type  =  'NX US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_5_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+str(f_usr_NX_US_rm)+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_6_rm) and os.path.getsize(f_NX_full_usr_6_rm) > 0:
            user_type  =  'NX Gateway US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_6_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+str(f_usr_NX_Gateway_US_rm)+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
         
        if os.path.isfile(f_NX_full_usr_7_rm) and os.path.getsize(f_NX_full_usr_7_rm) > 0:
            user_type  =  'NX-Machining'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_7_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Machining_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+str(f_usr_NX_Machining_rm)+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_usr_8_rm) and os.path.getsize(f_NX_full_usr_8_rm) > 0:
            user_type  =  'NX Assemblies Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_8_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Assemblies_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Assemblies_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_9_rm) and os.path.getsize(f_NX_full_usr_9_rm) > 0:
            user_type  =  'NX CheckMate Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_9_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_CheckMate_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_CheckMate_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_10_rm) and os.path.getsize(f_NX_full_usr_10_rm) > 0:
            user_type  =  'NX Drafting Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_10_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Drafting_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Drafting_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_11_rm) and os.path.getsize(f_NX_full_usr_11_rm) > 0:
            user_type  =  'NX SolidModeling Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_11_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SolidModeling_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SolidModeling_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_12_rm) and os.path.getsize(f_NX_full_usr_12_rm) > 0:
            user_type  =  'NX Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_12_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_usr_13_rm) and os.path.getsize(f_NX_full_usr_13_rm) > 0:
            user_type  =  'NX Gateway Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_13_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
#############################Code below this line is edited by Rajesh More on 17 June 2021##################################################################
        if os.path.isfile(f_NX_full_usr_14_rm) and os.path.getsize(f_NX_full_usr_14_rm) > 0:
            user_type  =  'NX-AdvanceDesigner -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_14_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_ADVDES_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_usr_15_rm) and os.path.getsize(f_NX_full_usr_15_rm) > 0:
            user_type  =  'NX-Designer -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_15_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Designer_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_usr_16_rm) and os.path.getsize(f_NX_full_usr_16_rm) > 0:
            user_type  =  'NX-Designer -Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_16_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Designer_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_usr_17_rm) and os.path.getsize(f_NX_full_usr_17_rm) > 0:
            user_type  =  'NX-AdvanceDesigner-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_17_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_AdvanceDesigner_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************")   

        if os.path.isfile(f_NX_full_usr_18_rm) and os.path.getsize(f_NX_full_usr_18_rm) > 0:
            user_type  =  'NX-SC12500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_18_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC12500_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_NX_full_usr_19_rm) and os.path.getsize(f_NX_full_usr_19_rm) > 0:
            user_type  =  'NX-SC12500-US-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_19_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC12500_US_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************")             
        
        if os.path.isfile(f_NX_full_usr_20_rm) and os.path.getsize(f_NX_full_usr_20_rm) > 0:
            user_type  =  'NX-SC13500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_20_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC13500_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_NX_full_usr_21_rm) and os.path.getsize(f_NX_full_usr_21_rm) > 0:
            user_type  =  'NX-SC13500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_21_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_SC13500_US_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_NX_full_usr_22_rm) and os.path.getsize(f_NX_full_usr_22_rm) > 0:
            user_type  =  'NX-GMS4010'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_22_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_GMS4010_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************")    

        if os.path.isfile(f_NX_full_usr_23_rm) and os.path.getsize(f_NX_full_usr_23_rm) > 0:
            user_type  =  'NX-NX11100N'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_23_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NX11100N_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************")
            
        if os.path.isfile(f_NX_full_usr_24_rm) and os.path.getsize(f_NX_full_usr_24_rm) > 0:
            user_type  =  'NX-NX12100N'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_24_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NX12100N_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 


        if os.path.isfile(f_NX_full_usr_25_rm) and os.path.getsize(f_NX_full_usr_25_rm) > 0:
            user_type  =  'NX-NS5010-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_25_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NS5010_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 
        
        # if os.path.isfile(f_NX_full_usr_26_rm) and os.path.getsize(f_NX_full_usr_26_rm) > 0:
        #     user_type  =  'NX-NS5010-US'
        #     app_type   =  'CAD'
        #     app_name   =  'NX'
        #     data = pd.read_csv(f_NX_full_usr_26_rm, header=None)
        #     for index,row in data.iterrows():
        #         user_name = row[0] ##date
        #         #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
        #         sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_NS5010_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
        #         INSERT_TABLE = cs_ORACLE.execute(sql)
        #     print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_NX_full_usr_27_rm) and os.path.getsize(f_NX_full_usr_27_rm) > 0:
            user_type  =  'NX-Sheet_Metal-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_27_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Sheet_Metal_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_PTC_US_full_usr_28_rm) and os.path.getsize(f_PTC_US_full_usr_28_rm) > 0:
            user_type  =  'PTC US'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_usr_28_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_PTC_US_full_usr_29_rm) and os.path.getsize(f_PTC_US_full_usr_29_rm) > 0:
            user_type  =  'PTC Global'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_usr_29_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_PTC_US_full_usr_30_rm) and os.path.getsize(f_PTC_US_full_usr_30_rm) > 0:
            user_type  =  'PTC Regional'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_usr_30_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_Regional_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 

        if os.path.isfile(f_PTC_US_full_usr_31_rm) and os.path.getsize(f_PTC_US_full_usr_31_rm) > 0:
            user_type  =  'PTC ToolDesign'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_usr_31_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_NX_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_usr_PTC_ToolDesign_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
            print(" Successfull upto 2351***********************************************") 
###################### Code above this line is edited by Rajesh More on 17 Jun 2021########################################################################

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)     
        
        
        
        
        
        print('444444444444444444444444444')                
        if os.path.isfile(f_NX_full_lic_1) and os.path.getsize(f_NX_full_lic_1) > 0:
            license_type  =  'NX Assemblies US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_1, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_2) and os.path.getsize(f_NX_full_lic_2) > 0:
            license_type  =  'NX CheckMate US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_2, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_3) and os.path.getsize(f_NX_full_lic_3) > 0:
            license_type  =  'NX Drafting US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_3, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_4) and os.path.getsize(f_NX_full_lic_4) > 0:
            license_type  =  'NX SolidModeling US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_4, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_5) and os.path.getsize(f_NX_full_lic_5) > 0:
            license_type  =  'NX US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_5, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_6) and os.path.getsize(f_NX_full_lic_6) > 0:
            license_type  =  'NX Gateway US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_6, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_US+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_7) and os.path.getsize(f_NX_full_lic_7) > 0:
            license_type  =  'NX-Machining'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_7, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Machining+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Machining+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_8) and os.path.getsize(f_NX_full_lic_8) > 0:
            license_type  =  'NX Assemblies Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_8, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_9) and os.path.getsize(f_NX_full_lic_9) > 0:
            license_type  =  'NX CheckMate Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_9, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_10) and os.path.getsize(f_NX_full_lic_10) > 0:
            license_type  =  'NX Drafting Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_10, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_11) and os.path.getsize(f_NX_full_lic_11) > 0:
            license_type  =  'NX SolidModeling Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_11, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_12) and os.path.getsize(f_NX_full_lic_12) > 0:
            license_type  =  'NX Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_12, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_13) and os.path.getsize(f_NX_full_lic_13) > 0:
            license_type  =  'NX Gateway Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_13, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

###################################Code below this line is added by Rajesh More on 17 Jun 2021##############################################################################
        if os.path.isfile(f_NX_full_lic_14) and os.path.getsize(f_NX_full_lic_14) > 0:
            license_type  =  'NX-AdvanceDesigner -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_14, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_ADVDES_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_15) and os.path.getsize(f_NX_full_lic_15) > 0:
            license_type  =  'NX-Designer -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_15, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Designer_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)                

        if os.path.isfile(f_NX_full_lic_16) and os.path.getsize(f_NX_full_lic_16) > 0:
            license_type  =  'NX-Designer -Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_16, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Designer_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
                
        if os.path.isfile(f_NX_full_lic_17) and os.path.getsize(f_NX_full_lic_17) > 0:
            license_type  =  'NX-AdvanceDesigner-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_17, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_AdvanceDesigner_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        if os.path.isfile(f_NX_full_lic_18) and os.path.getsize(f_NX_full_lic_18) > 0:
            license_type  =  'NX-SC12500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_18, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC12500_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        if os.path.isfile(f_NX_full_lic_19) and os.path.getsize(f_NX_full_lic_19) > 0:
            license_type  =  'NX-SC12500-US-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_19, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC12500_US_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_20) and os.path.getsize(f_NX_full_lic_20) > 0:
            license_type  =  'NX-SC13500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_20, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC13500_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        if os.path.isfile(f_NX_full_lic_21) and os.path.getsize(f_NX_full_lic_21) > 0:
            license_type  =  'NX-SC13500-US-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_21, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC13500_US_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_22) and os.path.getsize(f_NX_full_lic_22) > 0:
            license_type  =  'NX-GMS4010'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_22, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_GMS4010+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        if os.path.isfile(f_NX_full_lic_23) and os.path.getsize(f_NX_full_lic_23) > 0:
            license_type  =  'NX-NX11100N'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_23, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NX11100N+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_24) and os.path.getsize(f_NX_full_lic_24) > 0:
            license_type  =  'NX-NX12100N'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_24, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NX12100N+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        
        if os.path.isfile(f_NX_full_lic_25) and os.path.getsize(f_NX_full_lic_25) > 0:
            license_type  =  'NX-NS5010-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_25, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NS5010_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        # if os.path.isfile(f_NX_full_lic_26) and os.path.getsize(f_NX_full_lic_26) > 0:
        #     license_type  =  'NX-NS5010-US'
        #     app_type   =  'CAD'
        #     app_name   =  'NX'
        #     data = pd.read_csv(f_NX_full_lic_26, sep=' ')
        #     for index,row in data.iterrows():
        #         date = row[0] ##date
        #         license_used = row[1]
        #         license_total = row[2]
        #         #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
        #         sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NS5010_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
        #         INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_27) and os.path.getsize(f_NX_full_lic_27) > 0:
            license_type  =  'NX-Sheet_Metal-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_27, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Sheet_Metal_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_PTC_US_full_lic_28) and os.path.getsize(f_PTC_US_full_lic_28) > 0:
            license_type  =  'PTC US'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_lic_28, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_US+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_PTC_US_full_lic_29) and os.path.getsize(f_PTC_US_full_lic_29) > 0:
            license_type  =  'PTC Global'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_lic_29, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_Global+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_PTC_US_full_lic_30) and os.path.getsize(f_PTC_US_full_lic_30) > 0:
            license_type  =  'PTC Regional'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_lic_30, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_Regional+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_PTC_US_full_lic_31) and os.path.getsize(f_PTC_US_full_lic_31) > 0:
            license_type  =  'PTC ToolDesign'
            app_type   =  'CAD'
            app_name   =  'PTC'
            data = pd.read_csv(f_PTC_US_full_lic_31, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_ToolDesign+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
############################## Code above this line is edited by Rajesh More###########################################################################





        if os.path.isfile(f_NX_full_lic_1_rm) and os.path.getsize(f_NX_full_lic_1_rm) > 0:
            license_type  =  'NX Assemblies US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_1_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_2_rm) and os.path.getsize(f_NX_full_lic_2_rm) > 0:
            license_type  =  'NX CheckMate US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_2_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_3_rm) and os.path.getsize(f_NX_full_lic_3_rm) > 0:
            license_type  =  'NX Drafting US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_3_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_4_rm) and os.path.getsize(f_NX_full_lic_4_rm) > 0:
            license_type  =  'NX SolidModeling US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_4_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_5_rm) and os.path.getsize(f_NX_full_lic_5_rm) > 0:
            license_type  =  'NX US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_5_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_6_rm) and os.path.getsize(f_NX_full_lic_6_rm) > 0:
            license_type  =  'NX Gateway US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_6_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_US_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_7_rm) and os.path.getsize(f_NX_full_lic_7_rm) > 0:
            license_type  =  'NX-Machining'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_7_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Machining_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Machining_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_8_rm) and os.path.getsize(f_NX_full_lic_8_rm) > 0:
            license_type  =  'NX Assemblies Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_8_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Assemblies_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_9_rm) and os.path.getsize(f_NX_full_lic_9_rm) > 0:
            license_type  =  'NX CheckMate Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_9_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_CheckMate_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_10_rm) and os.path.getsize(f_NX_full_lic_10_rm) > 0:
            license_type  =  'NX Drafting Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_10_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Drafting_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_11_rm) and os.path.getsize(f_NX_full_lic_11_rm) > 0:
            license_type  =  'NX SolidModeling Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_11_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SolidModeling_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_12_rm) and os.path.getsize(f_NX_full_lic_12_rm) > 0:
            license_type  =  'NX Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_12_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_13_rm) and os.path.getsize(f_NX_full_lic_13_rm) > 0:
            license_type  =  'NX Gateway Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_13_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

########################## Code below this line is edited by Rajesh More###########################################################################
        if os.path.isfile(f_NX_full_lic_14_rm) and os.path.getsize(f_NX_full_lic_14_rm) > 0:
            license_type  =  'NX-AdvanceDesigner -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_14_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_ADVDES_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_15_rm) and os.path.getsize(f_NX_full_lic_15_rm) > 0:
            license_type  =  'NX-Designer -US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_15_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Designer_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_16_rm) and os.path.getsize(f_NX_full_lic_16_rm) > 0:
            license_type  =  'NX-Designer -Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_16_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Designer_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
                                
        if os.path.isfile(f_NX_full_lic_17_rm) and os.path.getsize(f_NX_full_lic_17_rm) > 0:
            license_type  =  'NX-AdvanceDesigner-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_17_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_AdvanceDesigner_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_18_rm) and os.path.getsize(f_NX_full_lic_18_rm) > 0:
            license_type  =  'NX-SC12500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_18_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC12500_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_19_rm) and os.path.getsize(f_NX_full_lic_19_rm) > 0:
            license_type  =  'NX-SC12500-US-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_19_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC12500_US_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_20_rm) and os.path.getsize(f_NX_full_lic_20_rm) > 0:
            license_type  =  'NX-SC13500-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_lic_20_rm, sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC13500_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        if os.path.isfile(f_NX_full_lic_21_rm) and os.path.getsize(f_NX_full_lic_21_rm) > 0:
                    license_type  =  'NX-SC13500-US-Global'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_lic_21_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_SC13500_US_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_lic_22_rm) and os.path.getsize(f_NX_full_lic_22_rm) > 0:
                    license_type  =  'NX-GMS4010'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_lic_22_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_GMS4010_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql)
        if os.path.isfile(f_NX_full_lic_23_rm) and os.path.getsize(f_NX_full_lic_23_rm) > 0:
                    license_type  =  'NX-NX11100N'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_lic_23_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NX11100N_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql)
        if os.path.isfile(f_NX_full_lic_24_rm) and os.path.getsize(f_NX_full_lic_24_rm) > 0:
                    license_type  =  'NX-NX12100N'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_lic_24_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NX12100N_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql) 


        if os.path.isfile(f_NX_full_lic_25_rm) and os.path.getsize(f_NX_full_lic_25_rm) > 0:
                    license_type  =  'NX-NS5010-Global'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_lic_25_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NS5010_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql) 
        
        # if os.path.isfile(f_NX_full_lic_26_rm) and os.path.getsize(f_NX_full_lic_26_rm) > 0:
        #             license_type  =  'NX-NS5010-US'
        #             app_type   =  'CAD'
        #             app_name   =  'NX'
        #             data = pd.read_csv(f_NX_full_lic_26_rm, sep=' ')
        #             for index,row in data.iterrows():
        #                 date = row[0] ##date
        #                 license_used = row[1]
        #                 license_total = row[2]
        #                 #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
        #                 sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_NS5010_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
        #                 INSERT_TABLE = cs_ORACLE.execute(sql) 
                                              
        if os.path.isfile(f_NX_full_lic_27_rm) and os.path.getsize(f_NX_full_lic_27_rm) > 0:
                    license_type  =  'NX-Sheet_Metal-Global'
                    app_type   =  'CAD'
                    app_name   =  'NX'
                    data = pd.read_csv(f_NX_full_lic_27_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Sheet_Metal_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql) 

        if os.path.isfile(f_PTC_US_full_lic_28_rm) and os.path.getsize(f_PTC_US_full_lic_28_rm) > 0:
                    license_type  =  'PTC US'
                    app_type   =  'CAD'
                    app_name   =  'PTC'
                    data = pd.read_csv(f_PTC_US_full_lic_28_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_US_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql) 

        if os.path.isfile(f_PTC_US_full_lic_29_rm) and os.path.getsize(f_PTC_US_full_lic_29_rm) > 0:
                    license_type  =  'PTC Global'
                    app_type   =  'CAD'
                    app_name   =  'PTC'
                    data = pd.read_csv(f_PTC_US_full_lic_29_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_Global_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql) 

        if os.path.isfile(f_PTC_US_full_lic_30_rm) and os.path.getsize(f_PTC_US_full_lic_30_rm) > 0:
                    license_type  =  'PTC Regional'
                    app_type   =  'CAD'
                    app_name   =  'PTC'
                    data = pd.read_csv(f_PTC_US_full_lic_30_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_Regional_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql) 

        if os.path.isfile(f_PTC_US_full_lic_31_rm) and os.path.getsize(f_PTC_US_full_lic_31_rm) > 0:
                    license_type  =  'PTC ToolDesign'
                    app_type   =  'CAD'
                    app_name   =  'PTC'
                    data = pd.read_csv(f_PTC_US_full_lic_31_rm, sep=' ')
                    for index,row in data.iterrows():
                        date = row[0] ##date
                        license_used = row[1]
                        license_total = row[2]
                        #sql = "insert into AAM_NX_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_NX_Gateway_Global_rm+"')"
                        sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_lic_PTC_ToolDesign_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                        INSERT_TABLE = cs_ORACLE.execute(sql) 
############################# Code above is edited by Rajesh More #########################################################################################




          
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)    
        
        if os.path.isfile(f_DFMPro_full_usr) and os.path.getsize(f_DFMPro_full_usr) > 0:
            user_type  =  'DFMPro Users'
            app_type   =  'CAD'
            app_name   =  'DFMPro'
            data = pd.read_csv(f_DFMPro_full_usr, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
            #sql = "insert into AAM_DFMPro_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_DFMPro_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_DFMPro_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)

        if os.path.isfile(f_DFMPro_full_usr_rm) and os.path.getsize(f_DFMPro_full_usr_rm) > 0:
            user_type  =  'DFMPro Users'
            app_type   =  'CAD'
            app_name   =  'DFMPro'
            data = pd.read_csv(f_DFMPro_full_usr_rm , header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
        #sql = "insert into AAM_DFMPro_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_DFMPro_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_DFMPro_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(prev_day_date))

        if os.path.isfile(f_DFMPro_full_license) and os.path.getsize(f_DFMPro_full_license) > 0:
            license_type  =  'DFMPro license'
            app_type   =  'CAD'
            app_name   =  'DFMPro'
            data = pd.read_csv(f_DFMPro_full_license,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_DFMPro_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_DFMPro_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_DFMPro_lincense+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_DFMPro_full_license_rm)) and (os.stat(f_DFMPro_full_license_rm).st_size != 0)):
            license_type  =  'DFMPro license'
            app_type   =  'CAD'
            app_name   =  'DFMPro'
            data = pd.read_csv(f_DFMPro_full_license_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
             #sql = "insert into AAM_DFMPro_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_DFMPro_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_DFMPro_lincense_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)


#################################################################################################################
#################################################################################################################

        if os.path.isfile(myfile_NX_AS5050_US_usr_full) and os.path.getsize(myfile_NX_AS5050_US_usr_full) > 0:
            user_type  =  'NX-AS5050-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_AS5050_US_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_AS5050_US_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 

        if os.path.isfile(myfile_NX_NS5010_Global_usr_full) and os.path.getsize(myfile_NX_NS5010_Global_usr_full) > 0:
            user_type  =  'NX-NS5010-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_NS5010_Global_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_NS5010_Global_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 

        if os.path.isfile(myfile_NX_UGID105_US_usr_full) and os.path.getsize(myfile_NX_UGID105_US_usr_full) > 0:
            user_type  =  'NX-UGID105-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID105_US_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_UGID105_US_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 

        if os.path.isfile(myfile_NX_UGID100_US_usr_full) and os.path.getsize(myfile_NX_UGID100_US_usr_full) > 0:
            user_type  =  'NX-UGID100-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID100_US_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_UGID100_US_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_Manufacturing_US_usr_full) and os.path.getsize(myfile_NX_Manufacturing_US_usr_full) > 0:
            user_type  =  'NX-Manufacturing_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_US_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_Manufacturing_US_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_Manufacturing_P1_US_usr_full) and os.path.getsize(myfile_NX_Manufacturing_P1_US_usr_full) > 0:
            user_type  =  'NX-Manufacturing_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_P1_US_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_Manufacturing_P1_US_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


##########################################


        if os.path.isfile(myfile_NX_AS5050_US_usr_full_rm) and os.path.getsize(myfile_NX_AS5050_US_usr_full_rm) > 0:
            user_type  =  'NX-AS5050-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_AS5050_US_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_AS5050_US_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 

        if os.path.isfile(myfile_NX_NS5010_Global_usr_full_rm) and os.path.getsize(myfile_NX_NS5010_Global_usr_full_rm) > 0:
            user_type  =  'NX-NS5010-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_NS5010_Global_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_NS5010_Global_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 

        if os.path.isfile(myfile_NX_UGID105_US_usr_full_rm) and os.path.getsize(myfile_NX_UGID105_US_usr_full_rm) > 0:
            user_type  =  'NX-UGID105-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID105_US_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_UGID105_US_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 

        if os.path.isfile(myfile_NX_UGID100_US_usr_full_rm) and os.path.getsize(myfile_NX_UGID100_US_usr_full_rm) > 0:
            user_type  =  'NX-UGID100-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID100_US_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_UGID100_US_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_Manufacturing_US_usr_full_rm) and os.path.getsize(myfile_NX_Manufacturing_US_usr_full_rm) > 0:
            user_type  =  'NX-Manufacturing_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_US_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_Manufacturing_US_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_Manufacturing_P1_US_usr_full_rm) and os.path.getsize(myfile_NX_Manufacturing_P1_US_usr_full_rm) > 0:
            user_type  =  'NX-Manufacturing_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_P1_US_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_Manufacturing_P1_US_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


############################################################
############################################################


        if os.path.isfile(myfile_All_Autodesk_Products_usr_full) and os.path.getsize(myfile_All_Autodesk_Products_usr_full) > 0:
            user_type  =  'All-Autodesk-Products'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_All_Autodesk_Products_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_All_Autodesk_Products_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_Autocad_Electrical_Mechanical_usr_full) and os.path.getsize(myfile_Autocad_Electrical_Mechanical_usr_full) > 0:
            user_type  =  'Autocad/Electrical/Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Autocad_Electrical_Mechanical_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_Autocad_Electrical_Mechanical_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_Inventor_Inventor_Pro_usr_full) and os.path.getsize(myfile_Inventor_Inventor_Pro_usr_full) > 0:
            user_type  =  'Inventor/Inventor-Pro'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Inventor_Inventor_Pro_usr_full, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_Inventor_Inventor_Pro_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


#############################################


        if os.path.isfile(myfile_All_Autodesk_Products_usr_full_rm) and os.path.getsize(myfile_All_Autodesk_Products_usr_full_rm) > 0:
            user_type  =  'All-Autodesk-Products'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_All_Autodesk_Products_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_All_Autodesk_Products_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_Autocad_Electrical_Mechanical_usr_full_rm) and os.path.getsize(myfile_Autocad_Electrical_Mechanical_usr_full_rm) > 0:
            user_type  =  'Autocad/Electrical/Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Autocad_Electrical_Mechanical_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_Autocad_Electrical_Mechanical_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_Inventor_Inventor_Pro_usr_full_rm) and os.path.getsize(myfile_Inventor_Inventor_Pro_usr_full_rm) > 0:
            user_type  =  'Inventor/Inventor-Pro'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Inventor_Inventor_Pro_usr_full_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_1+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_Inventor_Inventor_Pro_usr_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)


############################################################
############################################################


        if os.path.isfile(myfile_NX_AS5050_US_license_full) and os.path.getsize(myfile_NX_AS5050_US_license_full) > 0:
            license_type  =  'NX-AS5050-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_AS5050_US_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_AS5050_US_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_NS5010_Global_license_full) and os.path.getsize(myfile_NX_NS5010_Global_license_full) > 0:
            license_type  =  'NX-NS5010-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_NS5010_Global_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_NS5010_Global_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_UGID105_US_license_full) and os.path.getsize(myfile_NX_UGID105_US_license_full) > 0:
            license_type  =  'NX-UGID105-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID105_US_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_UGID105_US_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_UGID100_US_license_full) and os.path.getsize(myfile_NX_UGID100_US_license_full) > 0:
            license_type  =  'NX-UGID100-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID100_US_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_UGID100_US_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_Manufacturing_US_license_full) and os.path.getsize(myfile_NX_Manufacturing_US_license_full) > 0:
            license_type  =  'NX-Manufacturing_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_US_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_Manufacturing_US_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_Manufacturing_P1_US_license_full) and os.path.getsize(myfile_NX_Manufacturing_P1_US_license_full) > 0:
            license_type  =  'NX-Manufacturing_P1_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_P1_US_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_Manufacturing_P1_US_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


###########################################

        if os.path.isfile(myfile_NX_AS5050_US_license_full_rm) and os.path.getsize(myfile_NX_AS5050_US_license_full_rm) > 0:
            license_type  =  'NX-AS5050-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_AS5050_US_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_AS5050_US_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_NS5010_Global_license_full_rm) and os.path.getsize(myfile_NX_NS5010_Global_license_full_rm) > 0:
            license_type  =  'NX-NS5010-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_NS5010_Global_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_NS5010_Global_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_UGID105_US_license_full_rm) and os.path.getsize(myfile_NX_UGID105_US_license_full_rm) > 0:
            license_type  =  'NX-UGID105-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID105_US_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_UGID105_US_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_UGID100_US_license_full_rm) and os.path.getsize(myfile_NX_UGID100_US_license_full_rm) > 0:
            license_type  =  'NX-UGID100-US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_UGID100_US_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_UGID100_US_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


        if os.path.isfile(myfile_NX_Manufacturing_US_license_full_rm) and os.path.getsize(myfile_NX_Manufacturing_US_license_full_rm) > 0:
            license_type  =  'NX-Manufacturing_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_US_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_Manufacturing_US_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(myfile_NX_Manufacturing_P1_US_license_full_rm) and os.path.getsize(myfile_NX_Manufacturing_P1_US_license_full_rm) > 0:
            license_type  =  'NX-Manufacturing_P1_US'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(myfile_NX_Manufacturing_P1_US_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_Manufacturing_P1_US_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


###########################################################
 

        if os.path.isfile(myfile_All_Autodesk_Products_license_full) and os.path.getsize(myfile_All_Autodesk_Products_license_full) > 0:
            license_type  =  'All-Autodesk-Products'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_All_Autodesk_Products_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_All_Autodesk_Products_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 
 
        if os.path.isfile(myfile_Autocad_Electrical_Mechanical_license_full) and os.path.getsize(myfile_Autocad_Electrical_Mechanical_license_full) > 0:
            license_type  =  'Autocad/Electrical/Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Autocad_Electrical_Mechanical_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Autocad_Electrical_Mechanical_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)
 
 
        if os.path.isfile(myfile_Inventor_Inventor_Pro_license_full) and os.path.getsize(myfile_Inventor_Inventor_Pro_license_full) > 0:
            license_type  =  'Inventor/Inventor-Pro'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Inventor_Inventor_Pro_license_full,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Inventor_Inventor_Pro_license+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)


###########################################################
 

        if os.path.isfile(myfile_All_Autodesk_Products_license_full_rm) and os.path.getsize(myfile_All_Autodesk_Products_license_full_rm) > 0:
            license_type  =  'All-Autodesk-Products'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_All_Autodesk_Products_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_All_Autodesk_Products_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

 

        if os.path.isfile(myfile_Autocad_Electrical_Mechanical_license_full_rm) and os.path.getsize(myfile_Autocad_Electrical_Mechanical_license_full_rm) > 0:
            license_type  =  'Autocad/Electrical/Mechanical'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Autocad_Electrical_Mechanical_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Autocad_Electrical_Mechanical_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

 
        if os.path.isfile(myfile_Inventor_Inventor_Pro_license_full_rm) and os.path.getsize(myfile_Inventor_Inventor_Pro_license_full_rm) > 0:
            license_type  =  'Inventor/Inventor-Pro'
            app_type   =  'CAD'
            app_name   =  'Autocad'
            data = pd.read_csv(myfile_Inventor_Inventor_Pro_license_full_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_SOLIDWORKS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_SOLIDWORKS_lincense+"')" 
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Inventor_Inventor_Pro_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')"
                INSERT_TABLE = cs_ORACLE.execute(sql)

###########################################################

        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)		
	
##############################################################
#Code by SM
         # Inserting data into user staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into User Staging Table - NX-93100-Global')
####################################################################################################
        if os.path.isfile(f_NX_full_usr_19) and os.path.getsize(f_NX_full_usr_19) > 0:
            print('under if ................')
            user_type  =  'NX-93100-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_19, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
               # sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_NX_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if os.path.isfile(f_NX_full_usr_19_rm) and os.path.getsize(f_NX_full_usr_19_rm) > 0:
            user_type  =  'NX-93100-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_usr_19_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+ f_NX_usr_rm +"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        
        #License
        if os.path.isfile(f_NX_full_license_20) and os.path.getsize(f_NX_full_license_20) > 0:
            license_type  =  'NX-93100-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data2 = pd.read_csv(f_NX_full_license_20,sep=' ')
            for index2,row2 in data2.iterrows():
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_INVENTOR_INT_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_license+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        if  ((path.exists(f_NX_full_license_20_rm)) and (os.stat(f_NX_full_license_20_rm).st_size != 0)):
            license_type  =  'NX-93100-Global'
            app_type   =  'CAD'
            app_name   =  'NX'
            data = pd.read_csv(f_NX_full_license_20_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_NX_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        
        #cs_ORACLE.execute(MERGE_AAM_AUTOCAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
        print('start............')
#Catia Zone wise Report
# Inserting data into user staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into User Staging Table - Europe')
####################################################################################################
        #print('shashi 1 ****************************************************')
        if os.path.isfile(f_Catia_Zone_wise_Report_full_usr_21) and os.path.getsize(f_Catia_Zone_wise_Report_full_usr_21) > 0:
            #print('under if ................')
            #print('p_21 Value',p_21)
            user_type  =  'Europe'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_Catia_Zone_wise_Report_full_usr_21, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
               # sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_Catia_Zone_wise_Report_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)
#rm    
        #print('shashi 2 ****************************************************')           
        if os.path.isfile(f_Catia_Zone_wise_Report_full_usr_21_rm) and os.path.getsize(f_Catia_Zone_wise_Report_full_usr_21_rm) > 0:
            print('Shashi 2 under if ................')
            user_type  =  'Europe'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_Catia_Zone_wise_Report_full_usr_21_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+ f_Catia_Zone_wise_Report_usr_rm +"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        
#License
        #print('shashi 3 ****************************************************')           
        if os.path.isfile(f_Catia_Zone_wise_Report_full_license_22) and os.path.getsize(f_Catia_Zone_wise_Report_full_license_22) > 0:
            #print('Shashi 3 License print*********************************************')
            license_type  =  'Europe'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data2 = pd.read_csv(f_Catia_Zone_wise_Report_full_license_22,sep=' ')
            for index2,row2 in data2.iterrows():
                #print('row2:',row2)
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_INVENTOR_INT_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Catia_Zone_wise_Report_license+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        #print('shashi 4 ****************************************************')           
        if  ((path.exists(f_Catia_Zone_wise_Report_full_license_22_rm)) and (os.stat(f_Catia_Zone_wise_Report_full_license_22_rm).st_size != 0)):
            #print('Shashi 4 License print*********************************************')
            license_type  =  'Europe'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_Catia_Zone_wise_Report_full_license_22_rm,sep=' ')
            for index,row in data.iterrows():
                #print('row2:',row2)
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
                #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Catia_Zone_wise_Report_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        
        #cs_ORACLE.execute(MERGE_AAM_AUTOCAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)

#Germany
# Inserting data into user staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into User Staging Table - Germany')
####################################################################################################
        #print('shashi 5 ****************************************************')           

        if os.path.isfile(f_Germany_full_usr_23) and os.path.getsize(f_Germany_full_usr_23) > 0:
            #print('under if ................')
            user_type  =  'Germany'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_Germany_full_usr_23, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
               # sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_Germany_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        #print('shashi 6 ****************************************************')           

        if os.path.isfile(f_Germany_full_usr_23_rm) and os.path.getsize(f_Germany_full_usr_23_rm) > 0:
            #print('under Germany if..............................')
            user_type  =  'Germany'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_Germany_full_usr_23_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+ f_Germany_usr_rm +"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        
        #License
        #print('shashi 7 ****************************************************')           

        if os.path.isfile(f_Germany_full_license_24) and os.path.getsize(f_Germany_full_license_24) > 0:
            #print('under Germany license if..............................')
            license_type  =  'Germany'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data2 = pd.read_csv(f_Germany_full_license_24,sep=' ')
            for index2,row2 in data2.iterrows():
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_INVENTOR_INT_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Germany_license+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        #print('shashi 8 ****************************************************')           

        if  ((path.exists(f_Germany_full_license_24_rm)) and (os.stat(f_Germany_full_license_24_rm).st_size != 0)):
            #print('under Germany RM license if..............................')
            license_type  =  'Germany'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_Germany_full_license_24_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_Germany_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)
        
        #cs_ORACLE.execute(MERGE_AAM_AUTOCAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
  
# PBO Loop
# Inserting data into user staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into User Staging Table - PBO')
####################################################################################################

        #print('shashi 9 ****************************************************')           

        if os.path.isfile(f_PBO_full_usr_25) and os.path.getsize(f_PBO_full_usr_25) > 0:
            #print('under PBO if ................')
            user_type  =  'PBO'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_PBO_full_usr_25, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
               # sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PBO_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        #print('shashi 10 ****************************************************')           

        if os.path.isfile(f_PBO_full_usr_25_rm) and os.path.getsize(f_PBO_full_usr_25_rm) > 0:
            user_type  =  'PBO'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_PBO_full_usr_25_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+ f_PBO_usr_rm +"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        
        #License

        #print('shashi 11 ****************************************************')           

        if os.path.isfile(f_PBO_full_license_26) and os.path.getsize(f_PBO_full_license_26) > 0:
            license_type  =  'PBO'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data2 = pd.read_csv(f_PBO_full_license_26,sep=' ')
            for index2,row2 in data2.iterrows():
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_INVENTOR_INT_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PBO_license+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        #print('shashi 12 ****************************************************')           

        if  ((path.exists(f_PBO_full_license_26_rm)) and (os.stat(f_PBO_full_license_26_rm).st_size != 0)):
            license_type  =  'PBO'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_PBO_full_license_26_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_PBO_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        
        #cs_ORACLE.execute(MERGE_AAM_AUTOCAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
     
# US1 Loop
# Inserting data into user staging table
####################################################################################################
        Logger.start(log_info = 'Inserting Data Into User Staging Table - US1')
####################################################################################################

        #print('shashi 13 ****************************************************')           

        if os.path.isfile(f_US1_full_usr_27) and os.path.getsize(f_US1_full_usr_27) > 0:
            #print('under if ................')
            user_type  =  'US1'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_US1_full_usr_27, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
               # sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_US1_usr+"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        #print('shashi 14 ****************************************************')           

        if os.path.isfile(f_US1_full_usr_27_rm) and os.path.getsize(f_US1_full_usr_27_rm) > 0:
            user_type  =  'US1'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_US1_full_usr_27_rm, header=None)
            for index,row in data.iterrows():
                user_name = row[0] ##date
                #sql = "insert into AAM_PTC_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+f_PTC_usr_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_USER_DETAILS_STG (USER_NAME,USER_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values('"+ str(user_name)+"','"+str(user_type)+"','"+ f_US1_usr_rm +"','"+str(app_type)+"','"+str(app_name)+"')"
                #print(sql)
                INSERT_TABLE = cs_ORACLE.execute(sql)

        cs_ORACLE.execute(MERGE_AAM_CAD_USER_DETAILS.format(Curr_date_only))
        cs_ORACLE.execute(DELETE_AAM_CAD_USER_DETAILS_STG)
        
        #License

        #print('shashi 15 ****************************************************')           

        if os.path.isfile(f_US1_full_license_28) and os.path.getsize(f_US1_full_license_28) > 0:
            license_type  =  'US1'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data2 = pd.read_csv(f_US1_full_license_28,sep=' ')
            for index2,row2 in data2.iterrows():
                date = row2[0] ##date
                license_used = row2[1]
                license_total = row2[2]
                #sql2 = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date2)+","+str(license_used2)+","+str(license_total2)+",'"+license_type2+"','"+f_ACAD_INVENTOR_INT_lincense+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_US1_license+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)


        #print('shashi 16 ****************************************************')           

        if  ((path.exists(f_US1_full_license_28_rm)) and (os.stat(f_US1_full_license_28_rm).st_size != 0)):
            license_type  =  'US1'
            app_type   =  'CAD'
            app_name   =  'Catia Zone wise Report'
            data = pd.read_csv(f_US1_full_license_28_rm,sep=' ')
            for index,row in data.iterrows():
                date = row[0] ##date
                license_used = row[1]
                license_total = row[2]
        #sql = "insert into AAM_AUTOCAD_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_ACAD_INVENTOR_INT_lincense_rm+"')"
                sql = "insert into AAM_CAD_CAE_ECS_LICENSES_DETAILS_STG (DATA_CAPTURE_DATE_TIME,LICENSES_IN_USE,LICENSES_AVAILABLE,LICENSE_TYPE,FILE_NAME,APP_TYPE,APP_NAME) values("+ convert_to_date(date)+","+str(license_used)+","+str(license_total)+",'"+license_type+"','"+f_US1_license_rm+"','"+str(app_type)+"','"+str(app_name)+"')" 
                INSERT_TABLE = cs_ORACLE.execute(sql)

        
        #cs_ORACLE.execute(MERGE_AAM_AUTOCAD_LICENSE_DETAILS.format(Curr_date_time))
        cs_ORACLE.execute(MERGE_AAM_CAD_LICENSE_DETAILS.format(Curr_date_time))
        
        cs_ORACLE.execute(DELETE_AAM_CAD_LICENSES_DETAILS_STG)
# End Three Loop

        print('end loop*************************************')
    
 
#End
############################################################### 
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
        print ("end time: ")
        print (now.strftime("%Y-%m-%d %H:%M:%S"))

    client = boto3.client('s3', aws_access_key_id=cdtls.aws_s3.aws_access_key_id,aws_secret_access_key=cdtls.aws_s3.aws_secret_access_key)
    transfer = S3Transfer(client)

    # Previous day Users files transfered to AWS loaction
####################################################################################################
    Logger.start(log_info = 'Previous Day Users Files Transferred To AWS Location')
####################################################################################################
    if  ((path.exists(f_PTC_full_usr_rm)) and (path.exists(f_PTC_full_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_rm, 'aam-ptc-files-oracle', f_PTC_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_rm)

    # Previous day License files transferd to AWS location
    if  ((path.exists(f_PTC_full_license_rm)) and (path.exists(f_PTC_full_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_rm, 'aam-ptc-files-oracle', f_PTC_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_rm)
        
        
    if  ((path.exists(f_PTC_full_usr_mathcad_rm)) and (path.exists(f_PTC_full_usr_mathcad))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_mathcad_rm, 'aam-ptc-files-oracle', f_PTC_usr_mathcad_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_mathcad_rm)

    # Previous day License files transferd to AWS location
    if  ((path.exists(f_PTC_full_license_mathcad_rm)) and (path.exists(f_PTC_full_license_mathcad))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_mathcad_rm, 'aam-ptc-files-oracle', f_PTC_lincense_mathcad_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_mathcad_rm)
        
        
    if  ((path.exists(f_PTC_full_usr_1_rm)) and (path.exists(f_PTC_full_usr_1))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_1_rm, 'aam-ptc-files-oracle', f_PTC_usr_1_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_1_rm)

    # Previous day License files transferd to AWS location
    if  ((path.exists(f_PTC_full_license_1_rm)) and (path.exists(f_PTC_full_license_1))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_1_rm, 'aam-ptc-files-oracle', f_PTC_lincense_1_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_1_rm)
        
    if  ((path.exists(f_PTC_full_usr_2_rm)) and (path.exists(f_PTC_full_usr_2))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_2_rm, 'aam-ptc-files-oracle', f_PTC_usr_2_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_usr_2_rm)

    # Previous day License files transferd to AWS location
    if  ((path.exists(f_PTC_full_license_2_rm)) and (path.exists(f_PTC_full_license_2))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_2_rm, 'aam-ptc-files-oracle', f_PTC_lincense_2_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PTC_lincense_2_rm)
        
#    if  ((path.exists(f_CATIA_full_usr_US_rm)) and (path.exists(f_CATIA_full_usr_US))):
#        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_usr_US_rm, 'aam-catia-files-oracle', f_CATIA_usr_US_rm)
#        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_usr_US_rm)

    if  ((path.exists(f_CATIA_full_usr_NonUS_rm)) and (path.exists(f_CATIA_full_usr_NonUS))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_usr_NonUS_rm, 'aam-catia-files-oracle', f_CATIA_usr_NonUS_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_usr_NonUS_rm)


    # Previous day License files transferd to AWS location
    if  ((path.exists(f_CATIA_full_license_US_rm)) and (path.exists(f_CATIA_full_license_US))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_lincense_US_rm, 'aam-catia-files-oracle', f_CATIA_lincense_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_lincense_US_rm)


    if  ((path.exists(f_CATIA_full_license_NonUS_rm)) and (path.exists(f_CATIA_full_license_NonUS))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_lincense_NonUS_rm, 'aam-catia-files-oracle', f_CATIA_lincense_NonUS_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_CATIA_lincense_NonUS_rm)

    if  ((path.exists(f_SOLIDWORKS_full_usr_rm)) and (path.exists(f_SOLIDWORKS_full_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDWORKS_usr_rm, 'aam-solidworks-files-oracle', f_SOLIDWORKS_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDWORKS_usr_rm)

    # Previous day License files transferd to AWS location
    if  ((path.exists(f_SOLIDWORKS_full_license_rm)) and (path.exists(f_SOLIDWORKS_full_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDWORKS_lincense_rm, 'aam-solidworks-files-oracle', f_SOLIDWORKS_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDWORKS_lincense_rm)
        
    if  ((path.exists(f_SOLIDEDGE_full_usr_rm)) and (path.exists(f_SOLIDEDGE_full_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDEDGE_usr_rm, 'aam-solidworks-files-oracle', f_SOLIDEDGE_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDEDGE_usr_rm)

    # Previous day License files transferd to AWS location
    if  ((path.exists(f_SOLIDEDGE_full_license_rm)) and (path.exists(f_SOLIDEDGE_full_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDEDGE_lincense_rm, 'aam-solidworks-files-oracle', f_SOLIDEDGE_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_SOLIDEDGE_lincense_rm)


    # Previous day Users files transfered to AWS loaction
    if  ((path.exists(f_ACAD_full_usr_rm)) and (path.exists(f_ACAD_full_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_usr_rm, 'aam-autocad-files-oracle', f_ACAD_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_usr_rm)

    if  ((path.exists(f_ACAD_full_INVPROSA_usr_rm)) and (path.exists(f_ACAD_full_INVPROSA_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_usr_rm, 'aam-autocad-files-oracle', f_ACAD_INVPROSA_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_usr_rm)

    if  ((path.exists(f_ACAD_full_Mechanicl_usr_rm)) and (path.exists(f_ACAD_full_Mechanicl_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Mechanicl_usr_rm, 'aam-autocad-files-oracle', f_ACAD_Mechanicl_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Mechanicl_usr_rm)

    if  ((path.exists(f_ACAD_full_Electrical_usr_rm)) and (path.exists(f_ACAD_full_Electrical_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Electrical_usr_rm, 'aam-autocad-files-oracle', f_ACAD_Electrical_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Electrical_usr_rm)


    if  ((path.exists(f_ACAD_full_INT_usr_rm)) and (path.exists(f_ACAD_full_INT_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_INT_usr_rm, 'aam-autocad-files-oracle', f_ACAD_INVPROSA_INT_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_INT_usr_rm)

    if  ((path.exists(f_ACAD_full_USCAMHUM_usr_rm)) and (path.exists(f_ACAD_full_USCAMHUM_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_USCAMHCM_usr_rm, 'aam-autocad-files-oracle', f_ACAD_INVPROSA_USCAMHCM_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_USCAMHCM_usr_rm)

    # Previous day License files transferd to AWS location
    if  ((path.exists(f_ACAD_full_license_rm)) and (path.exists(f_ACAD_full_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_lincense_rm, 'aam-autocad-files-oracle', f_ACAD_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_lincense_rm)

    if  ((path.exists(f_ACAD_full_INVPROSA_license_rm)) and (path.exists(f_ACAD_full_INVPROSA_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_lincense_rm, 'aam-autocad-files-oracle', f_ACAD_INVPROSA_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVPROSA_lincense_rm)

    if  ((path.exists(f_ACAD_full_Mechanicl_license_rm)) and (path.exists(f_ACAD_full_Mechanicl_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Mechanicl_lincense_rm, 'aam-autocad-files-oracle', f_ACAD_Mechanicl_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Mechanicl_lincense_rm)


    if  ((path.exists(f_ACAD_full_Electrical_license_rm)) and (path.exists(f_ACAD_full_Electrical_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Electrical_lincense_rm, 'aam-autocad-files-oracle', f_ACAD_Electrical_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_Electrical_lincense_rm)

    if  ((path.exists(f_ACAD_full_INT_license_rm)) and (path.exists(f_ACAD_full_INT_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVENTOR_INT_lincense_rm, 'aam-autocad-files-oracle', f_ACAD_INVENTOR_INT_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVENTOR_INT_lincense_rm)
        
    if  ((path.exists(f_ACAD_full_USCAMHSM_license_rm)) and (path.exists(f_ACAD_full_USCAMHSM_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVENTOR_USCAMHSM_lincense_rm, 'aam-autocad-files-oracle', f_ACAD_INVENTOR_USCAMHSM_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_ACAD_INVENTOR_USCAMHSM_lincense_rm)
        
    # Previous day Users files transfered to AWS loaction
    if  ((path.exists(f_NX_full_usr_1_rm)) and (path.exists(f_NX_full_usr_1))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Assemblies_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_Assemblies_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Assemblies_US_rm)


    if  ((path.exists(f_NX_full_usr_2_rm)) and (path.exists(f_NX_full_usr_2))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_CheckMate_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_CheckMate_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_CheckMate_US_rm)

    if  ((path.exists(f_NX_full_usr_3_rm)) and (path.exists(f_NX_full_usr_3))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Drafting_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_Drafting_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Drafting_US_rm)


    if  ((path.exists(f_NX_full_usr_4_rm)) and (path.exists(f_NX_full_usr_4))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SolidModeling_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_SolidModeling_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SolidModeling_US_rm)


    if  ((path.exists(f_NX_full_usr_5_rm)) and (path.exists(f_NX_full_usr_5))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_US_rm)


    if  ((path.exists(f_NX_full_usr_6_rm)) and (path.exists(f_NX_full_usr_6))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Gateway_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_Gateway_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Gateway_US_rm)


    if  ((path.exists(f_NX_full_usr_7_rm)) and (path.exists(f_NX_full_usr_7))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Machining_rm, 'aam-nx-users-files-oracle',f_usr_NX_Machining_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Machining_rm)


    if  ((path.exists(f_NX_full_usr_8_rm)) and (path.exists(f_NX_full_usr_8))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Assemblies_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_Assemblies_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Assemblies_Global_rm)


    if  ((path.exists(f_NX_full_usr_9_rm)) and (path.exists(f_NX_full_usr_9))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_CheckMate_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_CheckMate_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_CheckMate_Global_rm)


    if  ((path.exists(f_NX_full_usr_10_rm)) and (path.exists(f_NX_full_usr_10))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Drafting_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_Drafting_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Drafting_Global_rm)


    if  ((path.exists(f_NX_full_usr_11_rm)) and (path.exists(f_NX_full_usr_11))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SolidModeling_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_SolidModeling_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SolidModeling_Global_rm)

    if  ((path.exists(f_NX_full_usr_12_rm)) and (path.exists(f_NX_full_usr_12))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Global_rm)

    if  ((path.exists(f_NX_full_usr_13_rm)) and (path.exists(f_NX_full_usr_13))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Gateway_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_Gateway_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Gateway_Global_rm)
        
###################################Rajesh More(Below)#######################################################################################        
    if  ((path.exists(f_NX_full_usr_14_rm)) and (path.exists(f_NX_full_usr_14))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_ADVDES_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_ADVDES_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_ADVDES_US_rm)   
        
    if  ((path.exists(f_NX_full_usr_15_rm)) and (path.exists(f_NX_full_usr_15))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Designer_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_Designer_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Designer_US_rm)

    if  ((path.exists(f_NX_full_usr_16_rm)) and (path.exists(f_NX_full_usr_16))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Designer_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_Designer_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Designer_Global_rm)
        
    if  ((path.exists(f_NX_full_usr_17_rm)) and (path.exists(f_NX_full_usr_17))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_AdvanceDesigner_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_AdvanceDesigner_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_AdvanceDesigner_Global_rm)  

    if  ((path.exists(f_NX_full_usr_18_rm)) and (path.exists(f_NX_full_usr_18))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC12500_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_SC12500_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC12500_US_rm)    
    
    if  ((path.exists(f_NX_full_usr_19_rm)) and (path.exists(f_NX_full_usr_19))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC12500_US_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_SC12500_US_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC12500_US_Global_rm)    

    if  ((path.exists(f_NX_full_usr_20_rm)) and (path.exists(f_NX_full_usr_20))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC13500_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_SC13500_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC13500_US_rm)    

    if  ((path.exists(f_NX_full_usr_21_rm)) and (path.exists(f_NX_full_usr_21))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC13500_US_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_SC13500_US_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_SC13500_US_Global_rm)
    
    if  ((path.exists(f_NX_full_usr_22_rm)) and (path.exists(f_NX_full_usr_22))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_GMS4010_rm, 'aam-nx-users-files-oracle',f_usr_NX_GMS4010_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_GMS4010_rm)
    
    if  ((path.exists(f_NX_full_usr_23_rm)) and (path.exists(f_NX_full_usr_23))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NX11100N_rm, 'aam-nx-users-files-oracle',f_usr_NX_NX11100N_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NX11100N_rm)
    
    if  ((path.exists(f_NX_full_usr_24_rm)) and (path.exists(f_NX_full_usr_24))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NX12100N_rm, 'aam-nx-users-files-oracle',f_usr_NX_NX12100N_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NX12100N_rm)               

    if  ((path.exists(f_NX_full_usr_25_rm)) and (path.exists(f_NX_full_usr_25))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NS5010_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_NS5010_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NS5010_Global_rm) 

    # if  ((path.exists(f_NX_full_usr_26_rm)) and (path.exists(f_NX_full_usr_26))):
    #     transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NS5010_US_rm, 'aam-nx-users-files-oracle',f_usr_NX_NS5010_US_rm)
    #     os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_NS5010_US_rm) 

    if  ((path.exists(f_NX_full_usr_27_rm)) and (path.exists(f_NX_full_usr_27))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Sheet_Metal_Global_rm, 'aam-nx-users-files-oracle',f_usr_NX_Sheet_Metal_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_NX_Sheet_Metal_Global_rm) 

    if  ((path.exists(f_PTC_US_full_usr_28_rm)) and (path.exists(f_PTC_full_usr_28))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_US_rm, 'aam-nx-users-files-oracle',f_usr_PTC_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_US_rm) 

    if  ((path.exists(f_PTC_US_full_usr_29_rm)) and (path.exists(f_PTC_full_usr_29))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_Global_rm, 'aam-nx-users-files-oracle',f_usr_PTC_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_Global_rm) 

    if  ((path.exists(f_PTC_US_full_usr_30_rm)) and (path.exists(f_PTC_full_usr_30))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_Regional_rm, 'aam-nx-users-files-oracle',f_usr_PTC_Regional_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_Regional_rm)   


    if  ((path.exists(f_PTC_US_full_usr_31_rm)) and (path.exists(f_PTC_full_usr_31))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_ToolDesign_rm, 'aam-nx-users-files-oracle',f_usr_PTC_ToolDesign_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_usr_PTC_ToolDesign_rm)        
#################################################################################################################################################



        
    if  ((path.exists(f_NX_full_lic_1_rm)) and (path.exists(f_NX_full_lic_1))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Assemblies_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Assemblies_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Assemblies_US_rm)


    if  ((path.exists(f_NX_full_lic_2_rm)) and (path.exists(f_NX_full_lic_2))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_CheckMate_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_CheckMate_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_CheckMate_US_rm)

    if  ((path.exists(f_NX_full_lic_3_rm)) and (path.exists(f_NX_full_lic_3))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Drafting_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Drafting_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Drafting_US_rm)


    if  ((path.exists(f_NX_full_lic_4_rm)) and (path.exists(f_NX_full_lic_4))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SolidModeling_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_SolidModeling_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SolidModeling_US_rm)


    if  ((path.exists(f_NX_full_lic_5_rm)) and (path.exists(f_NX_full_lic_5))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_US_rm)


    if  ((path.exists(f_NX_full_lic_6_rm)) and (path.exists(f_NX_full_lic_6))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Gateway_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Gateway_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Gateway_US_rm)


    if  ((path.exists(f_NX_full_lic_7_rm)) and (path.exists(f_NX_full_lic_7))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Machining_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Machining_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Machining_rm)

    if  ((path.exists(f_NX_full_lic_8_rm)) and (path.exists(f_NX_full_lic_8))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Assemblies_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Assemblies_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Assemblies_Global_rm)


    if  ((path.exists(f_NX_full_lic_9_rm)) and (path.exists(f_NX_full_lic_9))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_CheckMate_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_CheckMate_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_CheckMate_Global_rm)


    if  ((path.exists(f_NX_full_lic_10_rm)) and (path.exists(f_NX_full_lic_10))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Drafting_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Drafting_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Drafting_Global_rm)


    if  ((path.exists(f_NX_full_lic_11_rm)) and (path.exists(f_NX_full_lic_11))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SolidModeling_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_SolidModeling_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SolidModeling_Global_rm)

    if  ((path.exists(f_NX_full_lic_12_rm)) and (path.exists(f_NX_full_lic_12))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Global_rm)

    if  ((path.exists(f_NX_full_lic_13_rm)) and (path.exists(f_NX_full_lic_13))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Gateway_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Gateway_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Gateway_Global_rm)
############################### Rajesh More(Below)####################################################
    if  ((path.exists(f_NX_full_lic_14_rm)) and (path.exists(f_NX_full_lic_14))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_ADVDES_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_ADVDES_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_ADVDES_US_rm)

    if  ((path.exists(f_NX_full_lic_15_rm)) and (path.exists(f_NX_full_lic_15))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Designer_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Designer_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Designer_US_rm)

    if  ((path.exists(f_NX_full_lic_16_rm)) and (path.exists(f_NX_full_lic_16))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Designer_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Designer_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Designer_Global_rm)
        
    if  ((path.exists(f_NX_full_lic_17_rm)) and (path.exists(f_NX_full_lic_17))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_AdvanceDesigner_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_AdvanceDesigner_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_AdvanceDesigner_Global_rm)

    if  ((path.exists(f_NX_full_lic_18_rm)) and (path.exists(f_NX_full_lic_18))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC12500_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_SC12500_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC12500_US_rm)

    if  ((path.exists(f_NX_full_lic_19_rm)) and (path.exists(f_NX_full_lic_19))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC12500_US_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_SC12500_US_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC12500_US_Global_rm)

    
    if  ((path.exists(f_NX_full_lic_20_rm)) and (path.exists(f_NX_full_lic_20))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC13500_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_SC13500_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC13500_US_rm)

    if  ((path.exists(f_NX_full_lic_21_rm)) and (path.exists(f_NX_full_lic_21))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC13500_US_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_SC13500_US_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_SC13500_US_Global_rm)
    
    if  ((path.exists(f_NX_full_lic_22_rm)) and (path.exists(f_NX_full_lic_22))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_GMS4010_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_GMS4010_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_GMS4010_rm)
    
    if  ((path.exists(f_NX_full_lic_23_rm)) and (path.exists(f_NX_full_lic_23))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NX11100N_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_NX11100N_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NX11100N_rm)
    
    if  ((path.exists(f_NX_full_lic_24_rm)) and (path.exists(f_NX_full_lic_24))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NX12100N_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_NX12100N_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NX12100N_rm)

    if  ((path.exists(f_NX_full_lic_25_rm)) and (path.exists(f_NX_full_lic_25))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NS5010_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_NS5010_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NS5010_Global_rm)

    # if  ((path.exists(f_NX_full_lic_26_rm)) and (path.exists(f_NX_full_lic_26))):
    #     transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NS5010_US_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_NS5010_US_rm)
    #     os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_NS5010_US_rm)

    if  ((path.exists(f_NX_full_lic_27_rm)) and (path.exists(f_NX_full_lic_27))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Sheet_Metal_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_NX_Sheet_Metal_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_NX_Sheet_Metal_Global_rm)

    if  ((path.exists(f_PTC_US_full_lic_28_rm)) and (path.exists(f_PTC_US_full_lic_28))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_US_rm, 'aam-nx-licenses-files-oracle',f_lic_PTC_US_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_US_rm)
    
    if  ((path.exists(f_PTC_US_full_lic_29_rm)) and (path.exists(f_PTC_US_full_lic_29))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_Global_rm, 'aam-nx-licenses-files-oracle',f_lic_PTC_Global_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_Global_rm)
    
    if  ((path.exists(f_PTC_US_full_lic_30_rm)) and (path.exists(f_PTC_US_full_lic_30))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_Regional_rm, 'aam-nx-licenses-files-oracle',f_lic_PTC_Regional_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_Regional_rm)

    if  ((path.exists(f_PTC_US_full_lic_31_rm)) and (path.exists(f_PTC_US_full_lic_31))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_ToolDesign_rm, 'aam-nx-licenses-files-oracle',f_lic_PTC_ToolDesign_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_lic_PTC_ToolDesign_rm)
############################################### Rajesh More (ABove)########################################################
            
    if  ((path.exists(f_DFMPro_full_usr_rm)) and (path.exists(f_DFMPro_full_usr))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_DFMPro_usr_rm, 'aam-nx-licenses-files-oracle',f_DFMPro_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_DFMPro_usr_rm)

    if  ((path.exists(f_DFMPro_full_license_rm)) and (path.exists(f_DFMPro_full_license))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_DFMPro_lincense_rm, 'aam-nx-licenses-files-oracle',f_DFMPro_lincense_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_DFMPro_lincense_rm)
##########################################################################
#Code By SM
    if  ((path.exists(f_NX_full_usr_19_rm)) and (path.exists(f_NX_full_usr_19))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_NX_usr, 'aam-ptc-files-oracle', f_NX_usr)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_NX_usr)


    if  ((path.exists(f_NX_full_license_20_rm)) and (path.exists(f_NX_full_license_20))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_NX_license_rm, 'aam-ptc-files-oracle', f_NX_license_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_NX_license_rm)

    if  ((path.exists(f_Catia_Zone_wise_Report_full_usr_21_rm)) and (path.exists(f_Catia_Zone_wise_Report_full_usr_21_rm))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_Catia_Zone_wise_Report_usr, 'aam-ptc-files-oracle', f_Catia_Zone_wise_Report_usr)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_Catia_Zone_wise_Report_usr)


    if  ((path.exists(f_Catia_Zone_wise_Report_full_license_22_rm)) and (path.exists(f_Catia_Zone_wise_Report_full_license_22_rm))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_Catia_Zone_wise_Report_license_rm, 'aam-ptc-files-oracle', f_Catia_Zone_wise_Report_license_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_Catia_Zone_wise_Report_license_rm)
#Code by SM 
#Germany
    if  ((path.exists(f_Germany_full_usr_23_rm)) and (path.exists(f_Germany_full_usr_23))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_Germany_usr_rm, 'aam-nx-licenses-files-oracle',f_Germany_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_Germany_usr_rm)

    if  ((path.exists(f_Germany_full_license_24_rm)) and (path.exists(f_Germany_full_license_24))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_Germany_license_rm, 'aam-nx-licenses-files-oracle',f_Germany_license_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_Germany_license_rm)
        
#PBO      
    if  ((path.exists(f_PBO_full_usr_25_rm)) and (path.exists(f_PBO_full_usr_25))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PBO_usr_rm, 'aam-nx-licenses-files-oracle',f_PBO_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PBO_usr_rm)

    if  ((path.exists(f_PBO_full_license_26_rm)) and (path.exists(f_PBO_full_license_26))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_PBO_license_rm, 'aam-nx-licenses-files-oracle',f_PBO_license_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_PBO_license_rm)
     
#US1      
    if  ((path.exists(f_US1_full_usr_27_rm)) and (path.exists(f_US1_full_usr_27))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_US1_usr_rm, 'aam-nx-licenses-files-oracle',f_US1_usr_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_US1_usr_rm)

    if  ((path.exists(f_US1_full_license_28_rm)) and (path.exists(f_US1_full_license_28))):
        transfer.upload_file('/home/ec2-user/CAD/ORACLE/FILES/'+f_US1_license_rm, 'aam-nx-licenses-files-oracle',f_US1_license_rm)
        os.remove('/home/ec2-user/CAD/ORACLE/FILES/'+f_US1_license_rm)
    
#End
####################################################################################################
except Exception as e:
    Logger.update_error(error=e)  
finally:
    Logger.end(email_alert=True, email_to=['1486ed74.aam.onmicrosoft.com@amer.teams.ms'])
####################################################################################################