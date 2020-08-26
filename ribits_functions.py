######################################
##  ------------------------------- ##
##     Ribits to ESRI AGOL/Portal   ##
##  ------------------------------- ##
##    Written by:                   ##
#     David Shaeffer                ##
#     U.S. Army Corps of Engineers  ##
#     South Atlantic Division       ##
##  ------------------------------- ##
##   Last Edited on: 08-25-2020     ##
##  ------------------------------- ##
######################################

#This function compresses the geodatabase
def zipFileGeodatabase(inFileGeodatabase, newZipFN):
    import zipfile
    import os
    import glob 

    if not (os.path.exists(inFileGeodatabase)):
        return False

    if (os.path.exists(newZipFN)):
        os.remove(newZipFN)

    zipobj = zipfile.ZipFile(newZipFN,'w')

    for infile in glob.glob(inFileGeodatabase+"/*"):
        zipobj.write(infile, os.path.basename(inFileGeodatabase)+"/"+os.path.basename(infile), zipfile.ZIP_DEFLATED)
        print ("Zipping: "+infile)

    zipobj.close()

    return True

#this functions uploads a compressed geodatabase to ESRI AGOL or Portal
def uploadtoportal(address, usernname, password, name, path):
    import os

    print("Uploading Data to AGOL/Portal")
    # Connect to the GIS
    from arcgis.gis import GIS
    from arcgis import features

    import os

    # Connect to agol/portal
    try:
        gis = GIS(address, usernname, password, verify_cert=False)
        print("Successfully Connected to AGOL/Portal!")
    except Exception as e:
        print(e)

    try:
        #zip the geodatabase
        zipFileGeodatabase(path, path + ".zip")
        
        # Search for Feature Layers owned by the logged-in user
        my_csv = gis.content.search(query="owner:" + gis.users.me.username,
                                    item_type="Feature Layer Collection",
                                    max_items=50)
        existingtabl = False
        for record in my_csv:
            # print(record.title)
            if name in record.title:
                existingtabl = True

        # If there is not an existing table then upload the initial
        if existingtabl is False:

            item_prop = {'title': name, 'type': 'File Geodatabase'}
            print("Uploading " + name + " Geodatabase")
            csv_item = gis.content.add(item_properties=item_prop, data=path+".zip")
            print("Publishing " + name + " Geodatabase to a Hosted Feature Layer")
            impacts_item = csv_item.publish()
            print("Upload Complete!")
        else:
            print("Updating " + name + " Geodatabase")
            # overwrite the existing spreadsheet
            my_featurelayers = gis.content.search(query="owner:" + gis.users.me.username,
                                                  item_type="Feature Layer",
                                                  max_items=50)
            for features in my_featurelayers:

                if name in features.title:
                    feature_item = features

            from arcgis.features import FeatureLayerCollection
            flayer_collection = FeatureLayerCollection.fromitem(feature_item)

            try:
                # call the overwrite() method which can be accessed using the manager property
                flayer_collection.manager.overwrite(path+".zip")
            except Exception:
                e = sys.exc_info()[1]
                print(e)
                print("Exception 1")
            print("Upload Complete!")

    except Exception as e:
        print("Exception 2")
        print(e)

#This creates a file geodatabase based on a path
def creategdb(path):
    try:
        import arcpy
        import os
        # Set workspace
        arcpy.env.workspace = path
        #overwrite output if it already exists
        arcpy.env.overwriteOutput = True
        # Set local variables
        out_folder_path = os.path.dirname(path)
        out_name = os.path.basename(path)
        # Execute CreateFileGDB
        print("Creating file geodatabase")
        arcpy.CreateFileGDB_management(out_folder_path, out_name)
    except Exception as e:
        print (e)
        print("Could not create File Geodatabase!")

#This function creates a feature class from Ribits private bank site geojson webservice
def createbankfootprintfc(path):
    import json
    import urllib3
    import arcpy
    import os
    # create a pool manager
    http = urllib3.PoolManager()
    #disable HTTPS SSL warning
    urllib3.disable_warnings()
    # get all current bank program ids https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_list/
    program = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_list/')
    #load the response into json
    bankdata = json.loads(program.data)
    # create a dictionary of program IDs
    bankprogramIDs = []
    # Add all the IDs to the dictionary
    for items in bankdata['ITEMS']:
        #testing code
        # if items['BANK_ID'] == 537:
            bankprogramIDs.append(items['BANK_ID'])
    # Set arcpy workspace
    arcpy.env.workspace = path
    #overwrite output if it already exists
    arcpy.env.overwriteOutput = True
    #set the spatial reference
    sr = arcpy.SpatialReference(4326)
    #create the bank feature class
    arcpy.CreateFeatureclass_management(path, "BankFootprints", "POLYGON", "", "DISABLED", "DISABLED", sr)
    # add fields to the banks
    arcpy.AddField_management("BankFootprints", 'BANK_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'CHAIR', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'DISTRICT', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'FIELD_OFFICE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'NOAA_FISHERIES_REGION', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'STATE_LIST', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'COUNTY_LIST', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'PERMIT_NUMBER', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'YEAR_ESTABLISHED', "SHORT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'TOTAL_ACRES', "FLOAT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_STATUS', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_STATUS_DATE', "DATE", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_TYPE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'COMMENTS', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'RIBITS_URL_TO_BANK', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'SERVICE_AREA_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_SPONSOR_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_MANAGERS_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_MANAGERS_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_MANAGERS_TITLE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_MANAGERS_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_POCS_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_POCS_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_POCS_TITLE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_POCS_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankFootprints", 'BANK_POCS_TYPE', "TEXT", "", "", 6000)
    #set the field names
    fieldnames = ["BANK_NAME", "CHAIR", "DISTRICT", "FIELD_OFFICE", "NOAA_FISHERIES_REGION", "STATE_LIST", "COUNTY_LIST", "PERMIT_NUMBER", "YEAR_ESTABLISHED", "TOTAL_ACRES", 
    "BANK_STATUS", "BANK_STATUS_DATE", "BANK_TYPE", "COMMENTS", "RIBITS_URL_TO_BANK", "SERVICE_AREA_NAME", "BANK_SPONSOR_NAME", "BANK_MANAGERS_FIRST_NAME", "BANK_MANAGERS_LAST_NAME", 
    "BANK_MANAGERS_TITLE", "BANK_MANAGERS_PHONE", "BANK_POCS_FIRST_NAME", "BANK_POCS_LAST_NAME", "BANK_POCS_TITLE", "BANK_POCS_PHONE", "BANK_POCS_TYPE", "SHAPE@"]
    # for each program, get the data
    for IDs in bankprogramIDs:
        try:
            params = {"q": "{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
            # send the get request for each id
            r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_data/', fields=params)
            data = r.data
            bankdata = json.loads(data)
            for items in bankdata['ITEMS']:
                #make sure service area is not null
                    if 'BANK_FOOTPRINT' in items:
                        #loop through all service areas (primary, secondary, etc.) and add the polygon to the feature class
                        for areas in items['BANK_FOOTPRINT']:
                            #if geometry exsists then proceed
                            if 'GEOM' in areas.keys() and areas['GEOM'] != 'null':
                                #load geometry as json
                                geometry = json.loads(areas['GEOM'])
                                #create a empy list    
                                features = []
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
                                #handle the various geometry types
                                if geometry['type']=='Polygon':
                                    features.append(arcpy.AsShape(geometry))
                                    with arcpy.da.InsertCursor(os.path.abspath(path + "/BankFootprints"), fieldnames) as cursor:
                                        cursor.insertRow(features)
                                #multipolygon handler
                                elif geometry['type']=='MultiPolygon':
                                    for polys in geometry['coordinates']:
                                        geojson = {'type': 'Polygon', 'coordinates': polys}
                                        features.append(arcpy.AsShape(geojson))
                                        with arcpy.da.InsertCursor(os.path.abspath(path + "/BankFootprints"), fieldnames) as cursor:
                                            cursor.insertRow(features)
                                        #remove the geometry for the next polygon
                                        del features[-1]
                                elif geometry['type']=='GeometryCollection':
                                    #TODO handle Geometry Collection
                                    pass
                                elif geometry['type']=='LineString':
                                    #TODO handle LineString
                                    pass
                                else:
                                   print(geometry['type'] + " geometry type for " + str(items['BANK_ID']))
                            else:
                                    print("No bank footprint geometry for bank ID: " + str(items['BANK_ID']))               
        except Exception as e:
            print(e)
            print("Could not create bank footprint for ID: " + str(IDs))
    arcpy.RepairGeometry_management(os.path.abspath(path + "/BankFootprints"))
    return "Done creating bank footprints."

#This function creates a feature class from Ribits private bank centroids geojson
def createbankcentroidfc(path):
    import json
    import urllib3
    import arcpy
    import os
    # create a pool manager
    http = urllib3.PoolManager()
    #disable HTTPS SSL warning
    urllib3.disable_warnings()
    # get all current bank program ids https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_list/
    program = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_list/')
    #load the response into json
    bankdata = json.loads(program.data)
    # create a dictionary of program IDs
    bankprogramIDs = []
    # Add all the IDs to the dictionary
    for items in bankdata['ITEMS']:
        #testing code
        # if items['BANK_ID'] == 3105:
            bankprogramIDs.append(items['BANK_ID'])
    # Set workspace
    arcpy.env.workspace = path
    #overwrite output if it already exists
    arcpy.env.overwriteOutput = True
    #set the spatial reference
    sr = arcpy.SpatialReference(4326)
    #create the bank feature class
    arcpy.CreateFeatureclass_management(path, "BankCentroids", "POINT", "", "DISABLED", "DISABLED", sr)
    # add fields to the banks
    arcpy.AddField_management("BankCentroids", 'BANK_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'CHAIR', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'DISTRICT', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'FIELD_OFFICE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'NOAA_FISHERIES_REGION', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'STATE_LIST', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'COUNTY_LIST', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'PERMIT_NUMBER', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'YEAR_ESTABLISHED', "SHORT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'TOTAL_ACRES', "FLOAT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_STATUS', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_STATUS_DATE', "DATE", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_TYPE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'COMMENTS', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'RIBITS_URL_TO_BANK', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'SERVICE_AREA_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_SPONSOR_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_MANAGERS_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_MANAGERS_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_MANAGERS_TITLE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_MANAGERS_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_POCS_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_POCS_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_POCS_TITLE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_POCS_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankCentroids", 'BANK_POCS_TYPE', "TEXT", "", "", 6000)
    #set the field names
    fieldnames = ["BANK_NAME", "CHAIR", "DISTRICT", "FIELD_OFFICE", "NOAA_FISHERIES_REGION", "STATE_LIST", "COUNTY_LIST", "PERMIT_NUMBER", "YEAR_ESTABLISHED", "TOTAL_ACRES", 
    "BANK_STATUS", "BANK_STATUS_DATE", "BANK_TYPE", "COMMENTS", "RIBITS_URL_TO_BANK", "SERVICE_AREA_NAME", "BANK_SPONSOR_NAME", "BANK_MANAGERS_FIRST_NAME", "BANK_MANAGERS_LAST_NAME", 
    "BANK_MANAGERS_TITLE", "BANK_MANAGERS_PHONE", "BANK_POCS_FIRST_NAME", "BANK_POCS_LAST_NAME", "BANK_POCS_TITLE", "BANK_POCS_PHONE", "BANK_POCS_TYPE", "SHAPE@XY"]
    # for each program, get the data
    for IDs in bankprogramIDs:
        try:
            params = {"q": "{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
            # send the get request for each id
            r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_data/', fields=params)
            data = r.data
            bankdata = json.loads(data)
            for items in bankdata['ITEMS']:
                geometry = json.loads(items['BANK_LOCATION_CENTROID'])
                features = []
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
                features.append(arcpy.PointGeometry(arcpy.Point(geometry['coordinates'][0], geometry['coordinates'][1]), sr))
                # Write row to feature class
                with arcpy.da.InsertCursor(os.path.abspath(path + "/BankCentroids"), fieldnames) as cursor:
                    cursor.insertRow(features)
        except Exception as e:
            print(e)
            print("Could not create bank centroid for ID: " + str(IDs))
    return "Done creating bank centroids"

#This function creates a feature class from Ribits private bank site service area geojson webservice
def createbanksafc(path):
    import json
    import urllib3
    import arcpy
    import os
    # create a pool manager
    http = urllib3.PoolManager()
    #disable HTTPS SSL warning
    urllib3.disable_warnings()
    # get all current bank program ids https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_list/
    program = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_list/')
    #load the response into json
    bankdata = json.loads(program.data)
    # create a dictionary of program IDs
    bankprogramIDs = []
    # Add all the IDs to the dictionary
    # i=10
    for items in bankdata['ITEMS']:
        #testing code
        # if items['BANK_ID'] == 777:
            bankprogramIDs.append(items['BANK_ID'])
    # Set workspace
    arcpy.env.workspace = path
    #overwrite output if it already exists
    arcpy.env.overwriteOutput = True
    #set the spatial reference
    sr = arcpy.SpatialReference(4326)
    #create the bank feature class
    arcpy.CreateFeatureclass_management(path, "BankServiceAreas", "POLYGON", "", "DISABLED", "DISABLED", sr)
    # add fields to the banks
    arcpy.AddField_management("BankServiceAreas", 'BANK_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'CHAIR', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'DISTRICT', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'FIELD_OFFICE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'NOAA_FISHERIES_REGION', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'STATE_LIST', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'COUNTY_LIST', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'PERMIT_NUMBER', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'YEAR_ESTABLISHED', "SHORT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'TOTAL_ACRES', "FLOAT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_STATUS', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_STATUS_DATE', "DATE", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_TYPE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'COMMENTS', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'RIBITS_URL_TO_BANK', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'SERVICE_AREA_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_SPONSOR_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_MANAGERS_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_MANAGERS_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_MANAGERS_TITLE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_MANAGERS_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_POCS_FIRST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_POCS_LAST_NAME', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_POCS_TITLE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_POCS_PHONE', "TEXT", "", "", 6000)
    arcpy.AddField_management("BankServiceAreas", 'BANK_POCS_TYPE', "TEXT", "", "", 6000)
    #set the field names
    fieldnames = ["BANK_NAME", "CHAIR", "DISTRICT", "FIELD_OFFICE", "NOAA_FISHERIES_REGION", "STATE_LIST", "COUNTY_LIST", "PERMIT_NUMBER", "YEAR_ESTABLISHED", "TOTAL_ACRES", 
    "BANK_STATUS", "BANK_STATUS_DATE", "BANK_TYPE", "COMMENTS", "RIBITS_URL_TO_BANK", "SERVICE_AREA_NAME", "BANK_SPONSOR_NAME", "BANK_MANAGERS_FIRST_NAME", "BANK_MANAGERS_LAST_NAME", 
    "BANK_MANAGERS_TITLE", "BANK_MANAGERS_PHONE", "BANK_POCS_FIRST_NAME", "BANK_POCS_LAST_NAME", "BANK_POCS_TITLE", "BANK_POCS_PHONE", "BANK_POCS_TYPE", "SHAPE@"]
    # for each program, get the data
    for IDs in bankprogramIDs:
        try:
            params = {"q": "{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
            # send the get request for each id
            r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_data/', fields=params)
            data = r.data
            bankdata = json.loads(data)
            for items in bankdata['ITEMS']:
                    #make sure service area is not null
                    if items['SERVICE_AREAS'] is not None:
                        #loop through all service areas (primary, secondary, etc.) and add the polygon to the feature class
                        for areas in items['SERVICE_AREAS']:
                            # print(areas)
                            #if geometry exsists then proceed
                            if 'GEOM' in areas.keys():
                                #load geometry as json
                                geometry = json.loads(areas['GEOM'])
                                #create a empy list    
                                features = []
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

                                #handle the various geometry types
                                if geometry['type']=='Polygon':
                                    features.append(arcpy.AsShape(geometry))
                                    with arcpy.da.InsertCursor(os.path.abspath(path + "/BankServiceAreas"), fieldnames) as cursor:
                                        cursor.insertRow(features)
                                #multipolygon handler
                                elif geometry['type']=='MultiPolygon':
                                    for polys in geometry['coordinates']:
                                        geojson = {'type': 'Polygon', 'coordinates': polys}
                                        features.append(arcpy.AsShape(geojson))
                                        with arcpy.da.InsertCursor(os.path.abspath(path + "/BankServiceAreas"), fieldnames) as cursor:
                                            cursor.insertRow(features)
                                        #remove the geometry for the next polygon
                                        del features[-1]
                                elif geometry['type']=='GeometryCollection':
                                    #TODO handle Geometry Collection
                                    pass
                                elif geometry['type']=='LineString':
                                    #TODO handle LineString
                                    pass
                                else:
                                   print(geometry['type'] + " geometry type for " + str(items['BANK_ID']))
                            else:
                                print("No bank service area geometry for bank ID: " + str(items['BANK_ID']))               
        except Exception as e:
            print(e)
            print("Could not create bank service area for ID: " + str(IDs))
    #remove any bad geometry - normally invalid polygons
    arcpy.RepairGeometry_management(os.path.abspath(path + "/BankServiceAreas"))
    return "Done creating bank service areas."

### EXAMPLE USAGE ###

### BANKS ####
# COMPPLETE add the bank service area to the file geodatabase
# createbanksafc(r'C:\Users\k7rgrdls\Downloads\Ribits.gdb')

# COMPLETE create bankfoot print
# createbankfootprintfc(r'C:\Users\k7rgrdls\Downloads\Ribits.gdb')

# COMPLETE add the ILF centroid to file geodatabase
# createbankcentroidfc(r'C:\Users\k7rgrdls\Downloads\Ribits.gdb')

### ILF ####
#add ilf footprints to file geodatabase
#TODO

#add ilf program service area to file geodatabase
#TODO

#add ilf site service area to file geodatabase
#TODO

### Upload to AGOL/Portal ###

#upload the file geodatabase to ESRI AGOL/Portal
# uploadtoportal('https://AGOLPORTURL/portal/', 'AGOLPORTALUSERNAME', 'AGOLPORTALPASSWORD', 'FEATURECLASSNAME', r'C:\PATH\Ribits.gdb')
