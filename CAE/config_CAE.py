config ={
    # Revision history - 
    # Pravin Patil - 23 March 2023 - Application - 25 Features - 125
	#Pravin Patil - Rev 1 - 11 April 2023
	#Pravin Patil - Rev 2 - 20 April 2023
	# List of features removed from BI front End
	# - Abaqus2-Offtime-WHQ
	# - Abaqus2-Ontime-WHQ
	# - Abaqus-Abq_Prepost-Offtime-WHQ
	# - Abaqus-Abq_Prepost-Ontime-WHQ
	# - Abaqus-Abq_PrePost-WHQ
	# - Abaqus-Offtime-WHQ
	# - Abaqus-Ontime-PBO
	# - Abaqus-Ontime-EHQ
	# - Abaqus-Ontime-WHQ
	# - Abaqus-Prepost-Offtime-EHQ
	# - Abaqus-Prepost-Offtime-PBO
	# - Abaqus-Prepost-Offtime-WHQ
	# - Abaqus-Prepost-Ontime-EHQ
	# - Abaqus-Prepost-Ontime-PBO
	# - Abaqus-Prepost-Ontime-WHQ
	# - Adams-US
	# - Ansys_Electronics-Global
	# - Ansys-Global
	# - Ansys-Medini
	# - AnsysN-New(CAE)
	# - AnsysSpaceClaim-Global
	# - Comet
	# - APC_Hypemesh-Offtime-Regional
	# - APC_Hypemesh-Ontime-Regional
	# - Hyperworks-Offtime-EHQ
	# - Hyperworks-Offtime-US
	# - Hyperworks-Offtime-WHQ-PBO
	# - Hyperworks-Ontime-EHQ
	# - Hyperworks-Ontime-US
	# - Hyperworks-Ontime-WHQ-PBO
	# - Compose-APC_Regional
	# - Compose-APC_Regional-Offtime
	# - Compose-APC_Regional-Ontime
	# - Compose-Offtime-US
	# - Compose-Ontime-EHQ
	# - Compose-Ontime-US
	# - EmbedCode-APC_Regional-Offtime
	# - EmbedCode-APC_Regional-Ontime
	# - EmbedCode-Offtime-US
	# - EmbedCode-Ontime-EHQ
	# - EmbedCode-Ontime-US
	# - FluxGUI-APC_Regional-Offtime
	# - FluxGUI-APC_Regional-Ontime
	# - FluxGUI-Offtime-US
	# - FluxGUI-Ontime-EHQ
	# - FluxGUI-Ontime-US
	# - Inspire-APC_Regional-Offtime
	# - Inspire-APC_Regional-Ontime
	# - InspireCast-APC_Regional-Offtime
	# - InspireCast-APC_Regional-Ontime
	# - InspireCast-Offtime-US
	# - InspireCast-Ontime-EHQ
	# - InspireCast-Ontime-US
	# - InspireForm-APC_Regional-Offtime
	# - InspireForm-APC_Regional-Ontime
	# - InspireForm-Offtime-US
	# - InspireForm-Ontime-EHQ
	# - InspireForm-Ontime-US
	# - Inspire-Offtime-US
	# - Inspire-Ontime-EHQ
	# - Inspire-Ontime-US
	# - NcodeDesignLife-Ontime-EHQ
	# - OptiStruct-APC_Regional-Offtime
	# - OptiStruct-APC_Regional-Ontime
	# - OptiStruct-Offtime-US
	# - OptiStruct-Ontime-EHQ
	# - OptiStruct-Ontime-US
	# - SimSolid-APC_Regional
	# - SimSolid-APC_Regional-Offtime
	# - SimSolid-APC_Regional-Ontime
	# - SimSolid-EHQ
	# - SimSolid-Offtime-US
	# - SimSolid-Ontime-EHQ
	# - SimSolid-Ontime-US
	# - SimSolid-US
	# List of features Added in BI front End
    # - Adams_lease under Adams application
    # - LMS_TestLab
    # - Vcollab
    # - Flow3D
	# - Pravin Patil - Rev 2 - 20 April 2023 #
	# - Ansys-Q3DExtractor-CAE-US
	# - Ansys-TwinBuilderPro-CAE-US
	# - Ansys-AnsysMechanical-CAE-US
	# - Ansys-OptiSlang-CAE-US
	# - Ansys-Sherlock-CAE-US
	# - Ansys-RMxprt-CAE-US
	# - Ansys-HPCPack-CAE-US
	# - Ansys-Medini-ECS-US
	# - Ansys-Optislang-ECS-US
	# - Ansys-Electronics-ECS-US
	# - Ansys-Q3DExtractor-ECS-US
	# - Ansys-CFDPremium-ECS-US



    'Simlab':{
        'Simlab':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/simlab/log/",
            "user" : "Global-Simlab-users-",
            "license" : "Global-Simlab-licenses-",
        }
    },
 
    'FeSafe':{
        'FeSafe':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/fesafe/log/",
            "user" : "Global-fesafe-users-",
            "license" : "Global-fesafe-licenses-",
        }     
    },
 
    'NX Motion':{
        'NX Motion':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/NX_Motion/log/",
            "user" : "US_Sites-NX_Motion-users-",
            "license" : "US_Sites-NX_Motion-licenses-",
        }      
    },

    'Adams':{
        'Adams-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/adams/log/",
            "user" : "Global-Adams_Global-users-",
            "license" : "Global-Adams_Global-licenses-",
        },
#		Adams US is having only view and solver as two features so stopped tracking this one. - Pravin Patil 14 March 2023
#        'Adams-US':{
#            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/adams/log/",
#            "user" : "US_Sites-Adams-Global-Users-",
#            "license" : "US_Sites-Adams-Global-licenses-",
#        },

        'Adams-Solver-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/adams/log/",
            "user" : "US-Adams_Solver-users-",
            "license" : "US-Adams_Solver-licenses-",
        },
		
        'Adams-View-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/adams/log/",
            "user" : "US-Adams_View-users-",
            "license" : "US-Adams_View-licenses-",
        },
# New feature addtion in BI front End - Pravin Patil - 18 April 23 
        'Adams-Lease':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/adams/log/",
            "user" : "US_MSCONE-Adams-users-",
            "license" : "US_MSCONE-Adams-licenses-",
        }		
    },
  
    'StarCCM':{
        'StarCCM-Power US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/starccm/log/",
            "user" : "US-STARCCM_Power-Users-",
            "license" : "US-STARCCM_Power-licenses-",
        },

        'StarCCM-Suite US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/starccm/log/",
            "user" : "US-STARCCM_Suite-users-",
            "license" : "US-STARCCM_Suite-licenses-",
        }        
    },

    '3DCS':{
        '3DCS':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/3dcs/log/",
            "user" : "Global-3DCS-users-",
            "license" : "Global-3DCS-licenses-",
        }
    },
	
	#AAM discontinued have this application - Pravin Patil 14 March 2023
    #'Comet':{
    #    'Comet':{
    #        "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/comet/log/",
    #        "user" : "Global-Comet-users-",
    #        "license" : "Global-Comet-licenses-",
    #    }
    #    }

    'Masta':{
        'Masta':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/masta/log/",
            "user" : "Global-masta-users-",
            "license" : "Global-masta-licenses-",
        }
    },

    'AmeSim':{
        'AmeSim-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/amesim/log/",
            "user" : "Global-amesim-users-",
            "license" : "Global-amesim-licenses-",
        }
	},
	
    'AmeRun':{	
        'AmeRun-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/amesim/log/",
            "user" : "Global-amerun-users-",
            "license" : "Global-amerun-licenses-",
        }
    },
  
    'Femfat':{
        'Femfat':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/femfat/log/",
            "user" : "Global-FEMFAT-users-",
            "license" : "Global-FEMFAT-licenses-",
        }
    },

    'Ncode':{
        'Ncode-Automation-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ncode/log/",
            "user" : "Global-Automation-users-",
            "license" : "Global-Automation-licenses-",
        },
        
        'Ncode-Glyphworks-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ncode/log/",
            "user" : "Global-GlyphWorks-users-",
            "license" : "Global-GlyphWorks-licenses-",
        },
        
        'Ncode-Glyphworks-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ncode/log/",
            "user" : "US_Sites-GlyphWorks-users-",
            "license" : "US_Sites-Automation-licenses-",
        }
    },
	
    'Ansys':{
        'AnsysSpaceclaim-New':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-AnsysSpaceclaim-users-",
            "license" : "New-AnsysSpaceclaim-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23        
        # 'AnsysSpaceclaim-Global':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            # "user" : "Global-Ansys_spacelcaim-users-",
            # "license" : "Global-Ansys_spacelcaim-licenses-",
        # },
		
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'AnsysN-New':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            # "user" : "New-AnsysN-users-",
            # "license" : "New-AnsysN-licenses-",
        # },
        
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Ansys-Global':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            # "user" : "Global-Ansys-users-",
            # "license" : "Global-Ansys-licenses-",
        # },
        
        'Ansys_Electronics-New':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-AnsysElectronics-users-",
            "license" : "New-AnsysElectronics-licenses-",
        },
        
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Ansys_Electronics-Global':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            # "user" : "Global-Ansys_electronics-users-",
            # "license" : "Global-Ansys_electronics-licenses-",
        # },

# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Ansys-Medini':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            # "user" : "New-Medini-users-",
            # "license" : "New-Medini-licenses-",
        # },
        
        'Ansys-MotorCAD-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-Motorcad_ECS-users-",
            "license" : "US-Motorcad_ECS-licenses-",
        },
               
        'Ansys-MotorCADIM-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-MotorcadIM-users-",
            "license" : "New-MotorcadIM-licenses-",
        },
        
        'Ansys-MotorCADIM-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-MotorcadIM_ECS-users-",
            "license" : "US-MotorcadIM_ECS-licenses-",
        },
        
        'Ansys-MotorCADPM-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-MotorcadPM_ECS-users-",
            "license" : "US-MotorcadPM_ECS-licenses-",
        },
        
		 'Ansys-MotorCADPM-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-MotorcadPM-users-",
            "license" : "New-MotorcadPM-licenses-",
        },
        
        'Ansys-MotorCAD':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-Motorcad-users-",
            "license" : "New-Motorcad-licenses-",
        },
	#New_feature added -
        'Ansys-Q3DExtractor-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-Q3DExtractor-users-",
            "license" : "New-Q3DExtractor-licenses-",
        },
		
	#New_feature added -
        'Ansys-TwinBuilderPro-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-TwinBuilderPro-users-",
            "license" : "New-TwinBuilderPro-licenses-",
        },
		
	#New_feature added -
        'Ansys-AnsysMechanical-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-AnsysMechanical-users-",
            "license" : "New-AnsysMechanical-licenses-",
        },
	#New_feature added -
        'Ansys-MotorCADIM-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-MotorcadIM-users-",
            "license" : "New-MotorcadIM-licenses-",
        },
		
	#New_feature added -
        'Ansys-MotorCADPM-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-MotorcadPM-users-",
            "license" : "New-MotorcadPM-licenses-",
        },
		
	#New_feature added -
        'Ansys-OptiSlang-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-OptiSlang-users-",
            "license" : "New-OptiSlang-licenses-",
        },
		
	#New_feature added -
        'Ansys-Sherlock-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-Sherlock-users-",
            "license" : "New-Sherlock-licenses-",
        },
		
	#New_feature added -
        'Ansys-RMxprt-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-RMxprt-users-",
            "license" : "New-RMxprt-licenses-",
        },
		
	#New_feature added -
        'Ansys-HPCPack-CAE-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "New-HPCPack-users-",
            "license" : "New-HPCPack-licenses-",
        },
		
	#New_feature added -
        'Ansys-Medini-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-MotorcadPM_ECS-users-",
            "license" : "US-MotorcadPM_ECS-licenses-",
        },
		
	#New_feature added -
        'Ansys-Optislang-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-MotorcadPM_ECS-users-",
            "license" : "US-MotorcadPM_ECS-licenses-",
        },
		
	#New_feature added -
        'Ansys-Electronics-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-MotorcadPM_ECS-users-",
            "license" : "US-MotorcadPM_ECS-licenses-",
        },
		
	#New_feature added -
        'Ansys-Q3DExtractor-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-MotorcadPM_ECS-users-",
            "license" : "US-MotorcadPM_ECS-licenses-",
        },
		
	#New_feature added -
        'Ansys-CFDPremium-ECS-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansys/log/",
            "user" : "US-MotorcadPM_ECS-users-",
            "license" : "US-MotorcadPM_ECS-licenses-",
        },
    },
        
    'Avl':{
        'Avl':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/avl/log/",
            "user" : "Global-AVL-users-",
            "license" : "Global-AVL-licenses-",
        }
    },

    'Nx Nastran':{
        'NXNastran-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/nxnastran/log/",
            "user" : "Global-nxnastran-users-",
            "license" : "Global-nxnastran-licenses-",
        },
        
        'Acous_Model-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/nxnastran/log/",
            "user" : "Global-acous_model-users-",
            "license" : "Global-acous_model-licenses-",
        },
        
        'Acous_Mesh-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/nxnastran/log/",
            "user" : "Global-acous_mesh-users-",
            "license" : "Global-acous_mesh-licenses-",
        },
        
        'Acous_Adv-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/nxnastran/log/",
            "user" : "Global-acous_adv-users-",
            "license" : "Global-acous_adv-licenses-",
        },
        
        'Acous_pre-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/nxnastran/log/",
            "user" : "Global-acous_pre-users-",
            "license" : "Global-acous_pre-licenses-",
        },

        'Acous_hpc-Global':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/nxnastran/log/",
            "user" : "Global-acous_hpc-users-",
            "license" : "Global-acous_hpc-licenses-",
        }
    },
        
    'Speed':{
        'Speed':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/speed/log/",
            "user" : "US-SPEED-users-",
            "license" : "US-SPEED-licenses-",
        }
    },
	
    'ANSA':{
        'ANSA':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/ansa/log/",
            "user" : "US-ANSA-users-",
            "license" : "US-ANSA-licenses-",
        }
    },
	
    'Romax':{
        'Romax':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/romax/log/",
            "user" : "",
            "license" : "global-romax-licenses-",
        }
    },
	
    'Romax_WHQNT67':{
        'Romax_WHQNT67':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/romax_whqnt67/log/",
            "user" : "",
            "license" : "global-romax-licenses-",
        }
    },

    'Hypermesh':{
        'APC_Hyperworks-Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            "user" : "APC_Regional-HyperWorks-users-",
            "license" : "APC_Regional-HyperWorks-licenses-",
        },
        
# Removed from BI front End - Pravin Patil - 11 April 23
#        'APC_Hyperworks-Offtime-Regional':{
#           "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
#            "user" : "",
#            "license" : "APC_Regional-HyperWorks-licenses-offtime-",
#        },

# Removed from BI front End - Pravin Patil - 11 April 23       
        # 'APC_Hyperworks-Ontime-Regional':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            # "user" : "",
            # "license" : "APC_Regional-HyperWorks-licenses-ontime-",
        # },

# Removed from BI front End - Pravin Patil - 11 April 23        
        # 'Hyperworks-Offtime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-HyperWorks-licenses-offtime-",
        # },

# Removed from BI front End - Pravin Patil - 11 April 23        
        # 'Hyperworks-offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            # "user" : "",
            # "license" : "US_Sites-HyperWorks-licenses-offtime-",
        # },
		
# Removed from BI front End - Pravin Patil - 11 April 23         
        # 'Hyperworks-ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            # "user" : "",
            # "license" : "US_Sites-HyperWorks-licenses-ontime-",
        # },
        
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Hyperworks-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-HyperWorks-licenses-ontime-",
        # },
        
        'Hyperworks-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            "user" : "EHQ_Sites-HyperWorks-users-",
            "license" : "EHQ_Sites-HyperWorks-licenses-",
        },
        
        'Hyperworks-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            "user" : "US_Sites-HyperWorks-users-",
            "license" : "US_Sites-HyperWorks-licenses-",
        },

        'Hyperworks-WHQ-PBO':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            "user" : "Global-HyperWorks-users-",
            "license" : "Global-HyperWorks-licenses-",
        }

# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Hyperworks-Offtime-WHQ-PBO':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            # "user" : "",
            # "license" : "Global-HyperWorks-licenses-offtime-",
        # },

# Removed from BI front End - Pravin Patil - 11 April 23         
        # 'Hyperworks-Ontime-WHQ-PBO':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/hypermesh/log/",
            # "user" : "",
            # "license" : "Global-HyperWorks-licenses-ontime-",
        # }
    },
		
    'Isight':{
        'Isight':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/isight/log/",
            "user" : "Global-Isight-users-",
            "license" : "Global-Isight-licenses-",
        }
	},
	
    'Abaqus':{
        'Abaqus2-WHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "WHQ-Abaqus2-users-",
            "license" : "WHQ-Abaqus2-licenses-",
        },
        'Abaqus-Abq_PrePost-WHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "WHQ-Abq_PrePost-users-",
            "license" : "WHQ-Abq_PrePost-licenses-",
        },
        'Abaqus-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "EHQ-Abaqus-users-",
            "license" : "EHQ-Abaqus-licenses-",
        },
        'Abaqus-AHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "AHQ-Abaqus-users-",
            "license" : "AHQ-Abaqus-licenses-",
        },
        'Abaqus-FRA':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "FRA-Abaqus-users-",
            "license" : "FRA-Abaqus-licenses-",
        },
        'Abaqus-PBO':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "PBO-Abaqus-users-",
            "license" : "PBO-Abaqus-licenses-",	
        },
        'Abaqus-PrePost-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "EHQ-AbqPrePost-users-",
            "license" : "EHQ-AbqPrePost-licenses-",
        },
        'Abaqus-PrePost-FRA':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "FRA-AbqPrePost-users-",
            "license" : "FRA-AbqPrePost-licenses-",
        },
        'Abaqus-Prepost-PBO':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "PBO-AbqPrePost-users-",
            "license" : "PBO-AbqPrePost-licenses-",
        },
        'Abaqus-Prepost-WHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "WHQ-AbqPrePost-users-",
            "license" : "WHQ-AbqPrePost-licenses-",
        },
        'Abaqus-WHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            "user" : "WHQ-Abaqus-users-",
            "license" : "WHQ-Abaqus-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus2-Offtime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus2-Ontime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Abq_Prepost-Offtime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Abq_Prepost-Ontime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Offtime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Abq_Prepost-Ontime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Ontime-PBO':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Ontime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Prepost-Offtime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Prepost-Offtime-PBO':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Prepost-Offtime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Prepost-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Prepost-Ontime-PBO':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23
        # 'Abaqus-Prepost-Ontime-WHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/abaqus/log/",
            # "user" : "WHQ-Abaqus-users-",
            # "license" : "WHQ-Abaqus-licenses-",
        # }
	},
    'Endurica':{
        'Endurica':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/endurica/log/",
            "user" : "Global-Endurica-users-",
            "license" : "Global-Endurica-licenses-",
        }
	},	
    'Simerics':{
        'Simerics':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/simerics/log/",
            "user" : "Global-Simerics-users-",
            "license" : "Global-Simerics-licenses-",
        }
	},
    'Altair_Products':{
        'Compose-APC_Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "APC_Regional-Compose-users-",
            "license" : "APC_Regional-Compose-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Compose-APC_Regional-Offtime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-Compose-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Compose-APC_Regional-Ontime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-Compose-licenses-ontime-",
        # },
        'Compose-EHQ_Sites':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-Compose-users-",
            "license" : "EHQ_Sites-Compose-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Compose-Offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-Compose-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Compose-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-Compose-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Compose-Ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-Compose-licenses-ontime-",
        # },
        'Compose-US_Sites':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "US_Sites-Compose-users-",
            "license" : "US_Sites-Compose-licenses-",
        },
        'EmbedCode-APC_Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "APC_Regional-EmbedCode-users-",
            "license" : "APC_Regional-EmbedCode-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'EmbedCode-APC_Regional-Offtime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-EmbedCode-licenses-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'EmbedCode-APC_Regional-Ontime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-EmbedCode-licenses-ontime-",
        # },
        'EmbedCode-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-EmbedCode-users-",
            "license" : "EHQ_Sites-EmbedCode-licenses-",
        },
        'EmbedCode-US ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "US_Sites-EmbedCode-users-",
            "license" : "US_Sites-EmbedCode-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'EmbedCode-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-EmbedCode-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'EmbedCode-Ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-EmbedCode-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'EmbedCode-Offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-EmbedCode-licenses-offtime-",
        # },
        'FluxGUI-APC_Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "APC_Regional-FluxGUI-users-",
            "license" : "APC_Regional-FluxGUI-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'FluxGUI-APC_Regional-Offtime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-FluxGUI-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'FluxGUI-APC_Regional-Ontime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-FluxGUI-licenses-ontime-",
        # },
        'FluxGUI-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-FluxGUI-users-",
            "license" : "EHQ_Sites-FluxGUI-users-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'FluxGUI-Offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-FluxGUI-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'FluxGUI-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-FluxGUI-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'FluxGUI-Ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-FluxGUI-licenses-ontime-",
        # },
        'FluxGUI-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "US_Sites-FluxGUI-users-",
            "license" : "US_Sites-FluxGUI-licenses-",
        },
        'Inspire-APC_Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "APC_Regional-Inspire-users-",
            "license" : "APC_Regional-Inspire-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Inspire-APC_Regional-Offtime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-Inspire-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Inspire-APC_Regional-Ontime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-Inspire-licenses-ontime-",
        # },
        'InspireCast-APC_Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "APC_Regional-InspireCast-users-",
            "license" : "APC_Regional-InspireCast-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireCast-APC_Regional-Offtime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-InspireCast-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireCast-APC_Regional-Ontime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-InspireCast-licenses-ontime-",
        # },
        'Inspire-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-Inspire-users-",
            "license" : "EHQ_Sites-Inspire-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Inspire-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-Inspire-licenses-ontime-",
        # },
        'InspireCast-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-InspireCast-users-",
            "license" : "EHQ_Sites-InspireCast-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireCast-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-InspireCast-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireCast-Offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-InspireCast-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireCast-Ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-InspireCast-licenses-ontime-",
        # },
        'InspireCast-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "US_Sites-InspireCast-users-",
            "license" : "US_Sites-InspireCast-licenses-",
        },
        'InspireForm-APC_Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "APC_Regional-InspireForm-users-",
            "license" : "APC_Regional-InspireForm-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireForm-APC_Regional-Offtime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-InspireForm-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireForm-APC_Regional-Ontime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-InspireForm-licenses-ontime-",
        # },
        'InspireForm-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-InspireForm-users-",
            "license" : "EHQ_Sites-InspireForm-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireForm-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-InspireForm-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireForm-Ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-InspireForm-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'InspireForm-Offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-InspireForm-licenses-offtime-",
        # },
        'InspireForm-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "US_Sites-InspireForm-users-",
            "license" : "US_Sites-InspireForm-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Inspire-Offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-Inspire-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'Inspire-Ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-Inspire-licenses-ontime-",
        # },
        'Inspire-US_Sites':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "US_Sites-Inspire-users-",
            "license" : "US_Sites-Inspire-licenses-",
        },
        'NCodeDesignLife-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-NcodeDesignLife-users-",
            "license" : "EHQ_Sites-NcodeDesignLife-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'NcodeDesignLife-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-NcodeDesignLife-licenses-ontime-",
        # },
        'OptiStruct-APC_Regional':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "APC_Regional-OptiStruct-users-",
            "license" : "APC_Regional-OptiStruct-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'OptiStruct-APC_Regional-Offtime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-OptiStruct-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'OptiStruct-APC_Regional-Ontime':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "APC_Regional-OptiStruct-licenses-ontime-",
        # },
        'OptiStruct-EHQ':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "EHQ_Sites-OptiStruct-users-",
            "license" : "EHQ_Sites-OptiStruct-licenses-",
        },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'OptiStruct-Offtime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-OptiStruct-licenses-offtime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'OptiStruct-Ontime-EHQ':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "EHQ_Sites-OptiStruct-licenses-ontime-",
        # },
# Removed from BI front End - Pravin Patil - 11 April 23 
        # 'OptiStruct-Ontime-US':{
            # "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            # "user" : "",
            # "license" : "US_Sites-OptiStruct-licenses-ontime-",
        # },
        'OptiStruct-US':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/altair_products/log/",
            "user" : "US_Sites-OptiStruct-users-",
            "license" : "US_Sites-OptiStruct-licenses-",
        }
	},
# New application addtion in BI front End - Pravin Patil - 18 April 23 
    'Vcollab':{
        'Vcollab Pro':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/vcolab/log/",
            "user" : "Global-Vcolab-users-",
            "license" : "Global-Vcolab-licenses-",
        }
    },
# New application addtion in BI front End - Pravin Patil - 18 April 23 
    'Flow3D':{
        'Flow3D':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/flow3d/log/",
            "user" : "US-Flow3D_US-users-",
            "license" : "US-Flow3D_US-licenses-",
        }
    },
# New application addtion in BI front End - Pravin Patil - 18 April 23 
    'LMS_TestLab':{
        'LMS_TestLab':{
            "source": "caxrpt@10.0.130.36:/home/caxrpt/reportdata/lms_testlab/log/",
            "user" : "Global-testlab-users-",
            "license" : "Global-testlab-licenses-",
        }
    }
}
