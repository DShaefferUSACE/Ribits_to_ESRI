#This function creates a feature class from Ribits ILF service area geojson webservice
def createilfprogsafc(path):
    import json
    import urllib3
    import arcpy
    import os
    # create a pool manager
    http = urllib3.PoolManager()
    #disable HTTPS SSL warning
    urllib3.disable_warnings()
    # get all current ILF program ids https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_list/
    program = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_list/')
    #load the response into json
    programdata = json.loads(program.data)
    # create a dictionary of program IDs
    ilfprogramIDs = []
    # Add all the IDs to the dictionary
    for items in programdata['ITEMS']:
        ilfprogramIDs.append(items['PROGRAM_ID'])
        # print(items)
    # Set workspace
    arcpy.env.workspace = path
    #overwrite output if it already exists
    arcpy.env.overwriteOutput = True
    #set the spatial reference
    sr = arcpy.SpatialReference(4326)
    #create the ILF Service Areas feature class in the file geodatabase
    arcpy.CreateFeatureclass_management(path, "ILFProgramServiceArea", "POLYGON", "", "DISABLED", "DISABLED", sr)
    # add fields to the ILF Service areas
    arcpy.AddField_management("ILFProgramServiceArea", 'SERVICE_AREA_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'DISTRICT', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'FIELD_OFFICE', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'SECONDARY_OFFICES', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'NOAA_FISHERIES_REGION', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'STATES', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_STATUS', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_TYPE', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'WEBSITE', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'SPONSOR_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'SPONSOR_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_POCS_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_POCS_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_POCS_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_MANAGER_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_MANAGER_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'PROGRAM_MANAGER_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("ILFProgramServiceArea", 'RIBITS_URL_TO_PROGRAM', "TEXT", "", "", 6000)
    #set the field names
    fieldnames = ["SERVICE_AREA_NAME", "PROGRAM_NAME", "DISTRICT", "FIELD_OFFICE", "SECONDARY_OFFICES", "NOAA_FISHERIES_REGION", "STATES", 
    "PROGRAM_STATUS", "PROGRAM_TYPE", "WEBSITE", "SPONSOR_NAME", "SPONSOR_PHONE", "PROGRAM_POCS_FIRST_NAME", 
    "PROGRAM_POCS_LAST_NAME", "PROGRAM_POCS_PHONE", "PROGRAM_MANAGER_FIRST_NAME", "PROGRAM_MANAGER_LAST_NAME", 
    "PROGRAM_MANAGER_PHONE", "RIBITS_URL_TO_PROGRAM", "SHAPE@"]
    # for each program, get the data
    for IDs in ilfprogramIDs:
        try:
            params = {"q": "{\"program_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
            # send the get request for each id
            r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_data/', fields=params)
            data = r.data
            programdata = json.loads(data)
            for items in programdata['ITEMS']:
                #make sure service area is not null
                if str(items['SERVICE_AREAS']) != 'None':
                    #loop through all service areas (primary, secondary, etc.) and add the polygon to the feature class
                    for areas in items['SERVICE_AREAS']:
                        #if geometry exsists then proceed
                        if 'GEOM' in areas.keys():
                            #load geometry as json
                            geometry = json.loads(areas['GEOM'])
                            #handle the various geometry types
                            if geometry['type']=='Polygon':
                                geojson = geometry
                            elif geometry['type']=='MultiPolygon':
                                    geojson = { 
                                        "type": "Polygon",
                                        "coordinates": geometry['coordinates'][0]
                                        }
                            else:
                                geojson = None 
                                print(geometry['type'] + " geometry type!")
                            #create a empy list    
                            features = []
                            print("Going into feature extend")
                            # Add all the attributes
                            features.extend([
                            items['BANK_NAME'] if 'BANK_NAME' in items else 'NONE', 
                            items['CHAIR'] if 'CHAIR' in items else 'NONE', 
                            items['DISTRICT'] if 'DISTRICT' in items  else 'NONE', 
                            items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items else 'NONE',  
                            items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items else 'NONE', 
                            items['STATE_LIST'] if 'STATE_LIST' in items else 'NONE', 
                            items['COUNTY_LIST'] if 'COUNTY_LIST' in items else 'NONE', 
                            items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items else 'NONE', 
                            items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items else 0, 
                            items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items else 0, 
                            items['BANK_STATUS'] if 'BANK_STATUS' in items else 'NONE', 
                            items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items else '1/1/1700', 
                            items['BANK_TYPE'] if 'BANK_TYPE' in items else 'NONE', 
                            items['COMMENTS'] if 'COMMENTS' in items else 'NONE', 
                            items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items else 'NONE', 
                            items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE',
                            items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE', 
                            items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE', 
                            items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE', 
                            items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE', 
                            items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE',  
                            items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE', 
                            items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE', 
                            items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE', 
                            items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE', 
                            items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE'
                            ])
                            if geojson is not None:
                                #convert geojson to esri geometry
                                polygon = arcpy.AsShape(geojson)
                                features.append(polygon)
                                #insert feature data into feature class as a row
                                with arcpy.da.InsertCursor(os.path.abspath(path + "/ILFProgramServiceArea"), fieldnames) as cursor:
                                    cursor.insertRow(features)
                        else:
                            print("No ILF service area geometry for bank ID: " + str(items['BANK_ID']))  
        except Exception as e:
            print(e)
            print("Could not create ILF service area geometry!")
    #remove any bad geometry - normally invalid polygons
    arcpy.RepairGeometry_management(os.path.abspath(path + "/ILFProgramServiceArea"))
    return "Done creating ILF service areas."

createilfprogsafc(r'C:\Users\k7rgrdls\Downloads\Ribits.gdb')















# #This function creates a feature class from Ribits ILF mitigation site geojson webservice
# def createilffootprintfc(path):
#     import json
#     import urllib3
#     import arcpy
#     import os
#     # create a pool manager
#     http = urllib3.PoolManager()
#      #disable HTTPS SSL warning
#     urllib3.disable_warnings()
#     # get all current ILF program ids 
#     program = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_list/')
#     #load the response into json
#     programdata = json.loads(program.data)
#     # create a dictionary of program IDs
#     ilfprogramIDs = []
#     # Add all the IDs to the dictionary
#     for items in programdata['ITEMS']:
#         # if items['PROGRAM_ID'] == 181:
#             ilfprogramIDs.append(items['PROGRAM_ID'])
#         # for each program, get the program data
#     for IDs in ilfprogramIDs:
#         try:
#             params = {"q": "{\"program_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
#             # sed the get request for each id
#             r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_data/', fields=params)
#             data = r.data
#             sitedata = json.loads(data)
#             # create a dictionary of ILF site IDs
#             ilfsiteIDs = []
#             # Add all the ILF site IDs to the dictionary
#             for sites in sitedata['ITEMS']:
#                 for bankids in sites['PROGRAM_SITES']:
#                     #test code
#                     # if bankids['BANK_ID'] ==3651:
#                         ilfsiteIDs.append(bankids['BANK_ID'])
#             # Set workspace
#             arcpy.env.workspace = path
#             #overwrite output if it already exists
#             arcpy.env.overwriteOutput = True
#             #set the spatial reference
#             sr = arcpy.SpatialReference(4326)
#             #create a feature class inside the file geodatabase
#             arcpy.CreateFeatureclass_management(path, "ILFFootprints", "POLYGON", "", "DISABLED", "DISABLED", sr)
#             # add fields/atrributes to the ILF sites feature class
#             arcpy.AddField_management("ILFFootprints", 'BANK_NAME', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'CHAIR', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'DISTRICT', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'FIELD_OFFICE', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'NOAA_FISHERIES_REGION', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'STATE_LIST', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'COUNTY_LIST', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'PERMIT_NUMBER', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'YEAR_ESTABLISHED', "SHORT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'TOTAL_ACRES', "SHORT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_STATUS', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_STATUS_DATE', "DATE", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_TYPE', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'COMMENTS', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'RIBITS_URL_TO_BANK', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'SERVICE_AREA_NAME', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_SPONSOR_NAME', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_MANAGERS_FIRST_NAME', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_MANAGERS_LAST_NAME', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_MANAGERS_TITLE', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_MANAGERS_PHONE', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_POCS_FIRST_NAME', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_POCS_LAST_NAME', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_POCS_TITLE', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_POCS_PHONE', "TEXT", "", "", 6000)
#             arcpy.AddField_management("ILFFootprints", 'BANK_POCS_TYPE', "TEXT", "", "", 6000)
#             fieldnames = ["BANK_NAME", "CHAIR", "DISTRICT", "FIELD_OFFICE", "NOAA_FISHERIES_REGION", "STATE_LIST", "COUNTY_LIST", "PERMIT_NUMBER", "YEAR_ESTABLISHED", "TOTAL_ACRES", 
#             "BANK_STATUS", "BANK_STATUS_DATE", "BANK_TYPE", "COMMENTS", "RIBITS_URL_TO_BANK", "SERVICE_AREA_NAME", "BANK_SPONSOR_NAME", "BANK_MANAGERS_FIRST_NAME", "BANK_MANAGERS_LAST_NAME", 
#             "BANK_MANAGERS_TITLE", "BANK_MANAGERS_PHONE", "BANK_POCS_FIRST_NAME", "BANK_POCS_LAST_NAME", "BANK_POCS_TITLE", "BANK_POCS_PHONE", "BANK_POCS_TYPE", "SHAPE@"]
#             # for each program, get the program data
#             for IDs in ilfsiteIDs:
#                 try:
#                     # params = {"q": "{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
#                     # print("{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}")
#                     params = {"q": "{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
#                     # send the get request for each id
#                     r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_data/', fields=params)
#                     data = r.data
#                     bankdata = json.loads(data)
#                     for items in bankdata['ITEMS']:
#                         #make sure service area is not null
#                         if 'BANK_FOOTPRINT' in items:
#                             #loop through all service areas (primary, secondary, etc.) and add the polygon to the feature class
#                             for areas in items['BANK_FOOTPRINT']:
#                                 #if geometry exsists then proceed
#                                 if 'GEOM' in areas.keys() and areas['GEOM'] != 'null':
#                                     print("The geometry should be there!")
#                                     # print(items['BANK_FOOTPRINT'])
#                                     #load geometry as json
#                                     geometry = json.loads(areas['GEOM'])
#                                     print(geometry)
#                                     #if it is a polygon then use native geometry, otherwise use the first index
#                                     if geometry['type']=='Polygon':
#                                         geojson = geometry
#                                     elif geometry['type']=='MultiPolygon':
#                                         geojson = { 
#                                             "type": "Polygon",
#                                             "coordinates": geometry['coordinates'][0]
#                                             }
#                                     else:
#                                         print(geometry['type'] + " geometry type!")
#                                     #create a empy list    
#                                     features = []
#                                     features.extend([
#                                     items['BANK_NAME'] if 'BANK_NAME' in items else 'NONE', 
#                                     items['CHAIR'] if 'CHAIR' in items else 'NONE', 
#                                     items['DISTRICT'] if 'DISTRICT' in items  else 'NONE', 
#                                     items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items else 'NONE',  
#                                     items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items else 'NONE', 
#                                     items['STATE_LIST'] if 'STATE_LIST' in items else 'NONE', 
#                                     items['COUNTY_LIST'] if 'COUNTY_LIST' in items else 'NONE', 
#                                     items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items else 'NONE', 
#                                     items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items else 0, 
#                                     items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items else 0, 
#                                     items['BANK_STATUS'] if 'BANK_STATUS' in items else 'NONE', 
#                                     items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items else '1/1/1700', 
#                                     items['BANK_TYPE'] if 'BANK_TYPE' in items else 'NONE', 
#                                     items['COMMENTS'] if 'COMMENTS' in items else 'NONE', 
#                                     items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items else 'NONE', 
#                                     items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE',
#                                     items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE', 
#                                     items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE', 
#                                     items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE', 
#                                     items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE', 
#                                     items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE',  
#                                     items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE', 
#                                     items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE', 
#                                     items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE', 
#                                     items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE', 
#                                     items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE'
#                                     ])
#                                     print(geojson)
#                                     #convert geojson to esri geometry
#                                     polygon = arcpy.AsShape(geojson)
#                                     features.append(polygon)
#                                     #Add row to feature class
#                                     with arcpy.da.InsertCursor(os.path.abspath(path + "/ILFFootprints"), fieldnames) as cursor:
#                                         cursor.insertRow(features)
#                                 else:
#                                         print("No footprint geometry for bank ID: " + str(items['BANK_ID']))   
#                 except Exception as e:
#                     print(e)
#                     print("Could not create service area geometry! Bank ID: " + str(items['BANK_ID']))


#         except Exception as e:
#             print(e)
#             print("Could not get ILF sites!")

# createilffootprintfc(r'C:\Users\k7rgrdls\Downloads\Ribits.gdb')






































