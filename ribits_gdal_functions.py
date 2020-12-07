######################################
##  ------------------------------- ##
##  GDAL Ribits to ESRI AGOL/Portal ##
##  ------------------------------- ##
##    Written by:                   ##
#     David Shaeffer                ##
#     U.S. Army Corps of Engineers  ##
#     South Atlantic Division       ##
##  ------------------------------- ##
##   Last Edited on: 12-07-2020     ##
##  ------------------------------- ##
######################################

from osgeo import gdal
from osgeo import ogr
from osgeo import osr

#TODO zip the shapefile files

#TODO Upload to CWBI Portal

#This function creates a polygon shapefile from Ribits private bank service areas geojson webservice
def createbanksashp(path):
    try:
        import json
        import urllib3
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
        # set up the shapefile driver
        driver = ogr.GetDriverByName("ESRI Shapefile")
        # create the data source
        data_source = driver.CreateDataSource(path)
        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        # create the layer
        layer = data_source.CreateLayer("BankServiceAreas", srs, geom_type=ogr.wkbPolygon)
        # Add the fields 
        layer.CreateField(ogr.FieldDefn("BANKNAME", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("CHAIR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("DISTRICT", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("OFFICE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("NOAAREGION", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("STATES", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("COUNTYS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("PERMITNUM", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("YEAREST", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("TOTALACRES", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("BANKSTATUS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("STATUSDATE", ogr.OFTDate))
        layer.CreateField(ogr.FieldDefn("BANKTYPE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("COMMENTS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("RIBITSURL", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SERVAREA", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SPONSOR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTYPE", ogr.OFTString))
        # Add all the IDs to the dictionary
        for items in bankdata['ITEMS']:
            #testing code
            # if items['BANK_ID'] == 3005:
            # if items['BANK_ID'] == 3005 or items['BANK_ID'] == 4365:
                bankprogramIDs.append(items['BANK_ID'])
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
                        #loop through all service areas (primary, secondary, etc.) and add the polygon to the shapefile
                        for areas in items['SERVICE_AREAS']:
                            #if geometry exsists then proceed
                            if 'GEOM' in areas.keys():
                                #load geometry as json
                                geometry = json.loads(areas['GEOM'])
                                #handle the various geometry types
                                if geometry['type']=='Polygon':
                                    # pass
                                #create geometry
                                #initiate feature
                                    feature = ogr.Feature(layer.GetLayerDefn())
                                    #set field values
                                    feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                                    feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                    feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                    feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                    feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                    feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                    feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                    feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                    feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                    feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                    feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                                    feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                                    feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                                    feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                    feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                                    feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                    feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                                    feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                                    geojson = {'type': 'Polygon', 'coordinates': geometry['coordinates']}
                                    
                                    polygon = ogr.CreateGeometryFromJson(str(geojson))
                                    feature.SetGeometry(polygon)
                                    layer.CreateFeature(feature)
                                    # Dereference the feature
                                    feature = None
                                #multipolygon handler
                                elif geometry['type']=='MultiPolygon':
                                    
                                    for polys in geometry['coordinates']:
                                        #create geojson for each polygon
                                        #initiate feature
                                        feature = ogr.Feature(layer.GetLayerDefn())
                                        #set field values
                                        feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                                        feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                        feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                        feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                        feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                        feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                        feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                        feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                        feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                        feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                        feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                                        feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                                        feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                                        feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                        feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                                        feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                        feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                                        feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                                        geojson = {'type': 'Polygon', 'coordinates': polys}
                                        #create geometry from geojson
                                        polygon = ogr.CreateGeometryFromJson(str(geojson))
                                        feature.SetGeometry(polygon)
                                        layer.CreateFeature(feature)
                                        # Dereference the feature
                                        feature = None
                                elif geometry['type']=='GeometryCollection':
                                    #TODO handle Geometry Collection
                                    pass
                                elif geometry['type']=='LineString':
                                    #TODO handle LineString
                                    pass
                                else:
                                    print(geometry['type'] + " geometry type for " + str(items['BANK_ID']))
                                # feature = None
                            else:
                                print("No bank service area geometry for bank ID: " + str(items['BANK_ID']))   
            except Exception as e:
                print("Could not create bank service area for ID: " + str(IDs))
                import sys
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("Line Number and Error: " + str(line) + " " + str(e))
        # Save and close the data source
        data_source = None
        return "Done creating bank service areas."
    except Exception as e:
        print("Could not create bank service area shapefile: " + str(IDs))
        import sys
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print("Line Number and Error: " + str(line) + " " + str(e))

#This function creates a point and polygon shapefile from Ribits private bank sites data geojson webservice
def createbanksitesshp(path):
    try:
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
        # set up the shapefile driver
        driver = ogr.GetDriverByName("ESRI Shapefile")
        # create the data source
        data_source = driver.CreateDataSource(path)
        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        # create the layer
        layer = data_source.CreateLayer("BankFootprints", srs, geom_type=ogr.wkbPolygon)
        # create the centroid layer
        player = data_source.CreateLayer("BanksCentroids", srs, geom_type=ogr.wkbPoint)
        # Add the fields 
        layer.CreateField(ogr.FieldDefn("BANKNAME", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("CHAIR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("DISTRICT", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("OFFICE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("NOAAREGION", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("STATES", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("COUNTYS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("PERMITNUM", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("YEAREST", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("TOTALACRES", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("BANKSTATUS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("STATUSDATE", ogr.OFTDate))
        layer.CreateField(ogr.FieldDefn("BANKTYPE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("COMMENTS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("RIBITSURL", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SERVAREA", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SPONSOR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTYPE", ogr.OFTString))
        # add fields to centroid layer
        player.CreateField(ogr.FieldDefn("BANKNAME", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("CHAIR", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("DISTRICT", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("OFFICE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("NOAAREGION", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("STATES", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("COUNTYS", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("PERMITNUM", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("YEAREST", ogr.OFTInteger))
        player.CreateField(ogr.FieldDefn("TOTALACRES", ogr.OFTReal))
        player.CreateField(ogr.FieldDefn("BANKSTATUS", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("STATUSDATE", ogr.OFTDate))
        player.CreateField(ogr.FieldDefn("BANKTYPE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("COMMENTS", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("RIBITSURL", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("SERVAREA", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("SPONSOR", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRFIRST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRLAST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRTITLE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRPHONE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSFIRST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSLAST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSTITLE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSPHONE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSTYPE", ogr.OFTString))
        # Add all the IDs to the dictionary
        for items in bankdata['ITEMS']:
            #testing code
            # if items['BANK_ID'] == 537:
                bankprogramIDs.append(items['BANK_ID'])
        # for each program, get the data
        for IDs in bankprogramIDs:
            try:
                params = {"q": "{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
                # send the get request for each id
                r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_data/', fields=params)
                data = r.data
                bankdata = json.loads(data)
                for items in bankdata['ITEMS']:
                    if 'BANK_LOCATION_CENTROID' in items:
                        # print("Centroid!")
                        # print(items['BANK_LOCATION_CENTROID'])
                        geometry = json.loads(items['BANK_LOCATION_CENTROID'])
                        feature = ogr.Feature(player.GetLayerDefn())
                        #set field values
                        feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                        feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                        feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                        feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                        feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                        feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                        feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                        feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                        feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                        feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                        feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                        feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                        feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                        feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                        feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                        feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                        feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                        feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                        feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                        feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                        feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                        feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                        feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                        feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                        feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                        feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                        geojson = {'type': 'Point', 'coordinates': geometry['coordinates']}
                        
                        point = ogr.CreateGeometryFromJson(str(geojson))
                        feature.SetGeometry(point)
                        player.CreateFeature(feature)
                        # Dereference the feature
                        feature = None
                #make sure service area is not null
                    if 'BANK_FOOTPRINT' in items:
                        #loop through all service areas (primary, secondary, etc.) and add the polygon to the shapefile
                        for areas in items['BANK_FOOTPRINT']:
                            #if geometry exsists then proceed
                            if 'GEOM' in areas.keys() and areas['GEOM'] != 'null':
                                #load geometry as json
                                geometry = json.loads(areas['GEOM'])
                                #handle the various geometry types
                                if geometry['type']=='Polygon':
                                    # pass
                                #create geometry
                                #initiate feature
                                    feature = ogr.Feature(layer.GetLayerDefn())
                                    #set field values
                                    feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                                    feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                    feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                    feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                    feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                    feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                    feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                    feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                    feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                    feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                    feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                                    feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                                    feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                                    feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                    feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                                    feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                    feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                                    feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                                    feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                                    feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                                    geojson = {'type': 'Polygon', 'coordinates': geometry['coordinates']}
                                    
                                    polygon = ogr.CreateGeometryFromJson(str(geojson))
                                    feature.SetGeometry(polygon)
                                    layer.CreateFeature(feature)
                                    # Dereference the feature
                                    feature = None
                                #multipolygon handler
                                elif geometry['type']=='MultiPolygon':
                                    
                                    for polys in geometry['coordinates']:
                                        #create geojson for each polygon
                                        #initiate feature
                                        feature = ogr.Feature(layer.GetLayerDefn())
                                        #set field values
                                        feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                                        feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                        feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                        feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                        feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                        feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                        feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                        feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                        feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                        feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                        feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                                        feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                                        feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                                        feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                        feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                                        feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                        feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                                        feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                                        feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                                        feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                                        geojson = {'type': 'Polygon', 'coordinates': polys}
                                        #create geometry from geojson
                                        polygon = ogr.CreateGeometryFromJson(str(geojson))
                                        feature.SetGeometry(polygon)
                                        layer.CreateFeature(feature)
                                        # Dereference the feature
                                        feature = None
                                elif geometry['type']=='GeometryCollection':
                                    #TODO handle Geometry Collection
                                    pass
                                elif geometry['type']=='LineString':
                                    #TODO handle LineString
                                    pass
                                else:
                                    print(geometry['type'] + " geometry type for " + str(items['BANK_ID']))
                                # feature = None
                        else:
                            print("No bank footprint geometry for bank ID: " + str(items['BANK_ID']))              
            except Exception as e:
                print("Could not create bank footprint for ID: " + str(IDs))
                import sys
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("Line Number and Error: " + str(line) + " " + str(e))
        # Save and close the data source
        data_source = None
        return "Done creating bank footprints."
    except Exception as e:
                print("Could not create bank footprint area shapefile!")
                import sys
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("Line Number and Error: " + str(line) + " " + str(e))

#This function creates a polgyon shapefile from Ribits ILF program service areas geojson webservice
def createilfprogsashp(path):
    try:
        import json
        import urllib3
        import os
        # create a pool manager
        http = urllib3.PoolManager()
        #disable HTTPS SSL warning
        urllib3.disable_warnings()
        # get all current ILF program ids https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_list/
        program = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_list/')
        #load the response into json
        ILFdata = json.loads(program.data)
        # create a dictionary of program IDs
        ILFprogramIDs = []
        # set up the shapefile driver
        driver = ogr.GetDriverByName("ESRI Shapefile")
        # create the data source
        data_source = driver.CreateDataSource(path)
        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        # create the layer
        layer = data_source.CreateLayer("ILFProgramServiceAreas", srs, geom_type=ogr.wkbPolygon)
        # Add the fields 
        layer.CreateField(ogr.FieldDefn("PRGNAME", ogr.OFTString))
        # layer.CreateField(ogr.FieldDefn("CHAIR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("DISTRICT", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("OFFICE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("NOAAREGION", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("STATES", ogr.OFTString))
        # layer.CreateField(ogr.FieldDefn("COUNTYS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("PERMITNUM", ogr.OFTString))
        # layer.CreateField(ogr.FieldDefn("YEAREST", ogr.OFTInteger))
        # layer.CreateField(ogr.FieldDefn("TOTALACRES", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("STATUS", ogr.OFTString))
        # layer.CreateField(ogr.FieldDefn("STATUSDATE", ogr.OFTDate))
        layer.CreateField(ogr.FieldDefn("TYPE", ogr.OFTString))
        # layer.CreateField(ogr.FieldDefn("COMMENTS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("RIBITSURL", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SERVAREA", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SPONSOR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTYPE", ogr.OFTString))
        # Add all the IDs to the dictionary
        for items in ILFdata['ITEMS']:
            #testing code
            # if items['PROGRAM_ID'] == 3005:
            # if items['PROGRAM_ID'] == 3005 or items['PROGRAM_ID'] == 4365:
                ILFprogramIDs.append(items['PROGRAM_ID'])
        # print(ILFprogramIDs)
        for IDs in ILFprogramIDs:
            try:
                params = {"q": "{\"program_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
                # send the get request for each id
                r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_data/', fields=params)
                data = r.data
                ILFdata = json.loads(data)
                for items in ILFdata['ITEMS']:
                    #make sure service area is not null
                    if items['SERVICE_AREAS'] is not None:
                        #loop through all service areas (primary, secondary, etc.) and add the polygon to the feature class
                        for areas in items['SERVICE_AREAS']:
                            #if geometry exsists then proceed
                            if 'GEOM' in areas.keys():
                                #load geometry as json
                                geometry = json.loads(areas['GEOM'])
                                #handle the various geometry types
                                if geometry['type']=='Polygon':
                                    # pass
                                #create geometry
                                #initiate feature
                                    feature = ogr.Feature(layer.GetLayerDefn())
                                    #set field values
                                    feature.SetField("PRGNAME", items['PROGRAM_NAME'] if 'PROGRAM_NAME' in items and items['PROGRAM_NAME'] is not None else 'NONE')
                                    # feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                    feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                    feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                    feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                    feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                    # feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                    feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                    # feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                    # feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                    feature.SetField("STATUS", items['PROGRAM_STATUS'] if 'PROGRAM_STATUS' in items and items['PROGRAM_STATUS'] is not None else 'NONE')
                                    # feature.SetField("STATUSDATE", items['PROGRAM_STATUS_DATE'] if 'PROGRAM_STATUS_DATE' in items and items['PROGRAM_STATUS_DATE'] is not None else '1/1/1700')
                                    feature.SetField("TYPE", items['PROGRAM_TYPE'] if 'PROGRAM_TYPE' in items and items['PROGRAM_TYPE'] is not None else 'NONE')
                                    # feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                    feature.SetField("RIBITSURL", items['RIBITS_URL_TO_PROGRAM'] if 'RIBITS_URL_TO_PROGRAM' in items and items['RIBITS_URL_TO_PROGRAM'] is not None else 'NONE')
                                    feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                    feature.SetField("SPONSOR", items['PROGRAM_SPONSORS'][0]['SPONSOR_NAME'] if items['PROGRAM_SPONSORS'] is not None and 'SPONSOR_NAME' in items['PROGRAM_SPONSORS'][0] else 'NONE')
                                    feature.SetField("MNGRFIRST", items['PROGRAM_MANAGERS'][0]['FIRST_NAME'] if items['PROGRAM_MANAGERS'] is not None and 'FIRST_NAME' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRLAST", items['PROGRAM_MANAGERS'][0]['LAST_NAME'] if items['PROGRAM_MANAGERS'] is not None and 'LAST_NAME' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRTITLE", items['PROGRAM_MANAGERS'][0]['TITLE'] if items['PROGRAM_MANAGERS'] is not None and 'TITLE' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                    feature.SetField("MNGRPHONE", items['PROGRAM_MANAGERS'][0]['PHONE'] if items['PROGRAM_MANAGERS'] is not None and 'PHONE' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                    feature.SetField("POCSFIRST", items['PROGRAM_POCS'][0]['FIRST_NAME'] if items['PROGRAM_POCS'] is not None and 'FIRST_NAME' in items['PROGRAM_POCS'][0] else 'NONE')
                                    feature.SetField("POCSLAST", items['PROGRAM_POCS'][0]['LAST_NAME'] if items['PROGRAM_POCS'] is not None and 'LAST_NAME' in items['PROGRAM_POCS'][0] else 'NONE')
                                    feature.SetField("POCSTITLE", items['PROGRAM_POCS'][0]['TITLE'] if items['PROGRAM_POCS'] is not None and 'TITLE' in items['PROGRAM_POCS'][0] else 'NONE')
                                    feature.SetField("POCSPHONE", items['PROGRAM_POCS'][0]['PHONE'] if items['PROGRAM_POCS'] is not None and 'PHONE' in items['PROGRAM_POCS'][0] else 'NONE')
                                    feature.SetField("POCSTYPE", items['PROGRAM_POCS'][0]['POC_TYPE'] if items['PROGRAM_POCS'] is not None and 'POC_TYPE' in items['PROGRAM_POCS'][0] else 'NONE')

                                    geojson = {'type': 'Polygon', 'coordinates': geometry['coordinates']}
                                    
                                    polygon = ogr.CreateGeometryFromJson(str(geojson))
                                    feature.SetGeometry(polygon)
                                    layer.CreateFeature(feature)
                                    # Dereference the feature
                                    feature = None
                                #multipolygon handler
                                elif geometry['type']=='MultiPolygon':
                                    
                                    for polys in geometry['coordinates']:
                                        #create geojson for each polygon
                                        #initiate feature
                                        feature = ogr.Feature(layer.GetLayerDefn())
                                        #set field values
                                        feature.SetField("PRGNAME", items['PROGRAM_NAME'] if 'PROGRAM_NAME' in items and items['PROGRAM_NAME'] is not None else 'NONE')
                                        # feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                        feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                        feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                        feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                        feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                        # feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                        feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                        # feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                        # feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                        feature.SetField("STATUS", items['PROGRAM_STATUS'] if 'PROGRAM_STATUS' in items and items['PROGRAM_STATUS'] is not None else 'NONE')
                                        # feature.SetField("STATUSDATE", items['PROGRAM_STATUS_DATE'] if 'PROGRAM_STATUS_DATE' in items and items['PROGRAM_STATUS_DATE'] is not None else '1/1/1700')
                                        feature.SetField("TYPE", items['PROGRAM_TYPE'] if 'PROGRAM_TYPE' in items and items['PROGRAM_TYPE'] is not None else 'NONE')
                                        # feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                        feature.SetField("RIBITSURL", items['RIBITS_URL_TO_PROGRAM'] if 'RIBITS_URL_TO_PROGRAM' in items and items['RIBITS_URL_TO_PROGRAM'] is not None else 'NONE')
                                        feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                        feature.SetField("SPONSOR", items['PROGRAM_SPONSORS'][0]['SPONSOR_NAME'] if items['PROGRAM_SPONSORS'] is not None and 'SPONSOR_NAME' in items['PROGRAM_SPONSORS'][0] else 'NONE')
                                        feature.SetField("MNGRFIRST", items['PROGRAM_MANAGERS'][0]['FIRST_NAME'] if items['PROGRAM_MANAGERS'] is not None and 'FIRST_NAME' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRLAST", items['PROGRAM_MANAGERS'][0]['LAST_NAME'] if items['PROGRAM_MANAGERS'] is not None and 'LAST_NAME' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRTITLE", items['PROGRAM_MANAGERS'][0]['TITLE'] if items['PROGRAM_MANAGERS'] is not None and 'TITLE' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                        feature.SetField("MNGRPHONE", items['PROGRAM_MANAGERS'][0]['PHONE'] if items['PROGRAM_MANAGERS'] is not None and 'PHONE' in items['PROGRAM_MANAGERS'][0] else 'NONE')
                                        feature.SetField("POCSFIRST", items['PROGRAM_POCS'][0]['FIRST_NAME'] if items['PROGRAM_POCS'] is not None and 'FIRST_NAME' in items['PROGRAM_POCS'][0] else 'NONE')
                                        feature.SetField("POCSLAST", items['PROGRAM_POCS'][0]['LAST_NAME'] if items['PROGRAM_POCS'] is not None and 'LAST_NAME' in items['PROGRAM_POCS'][0] else 'NONE')
                                        feature.SetField("POCSTITLE", items['PROGRAM_POCS'][0]['TITLE'] if items['PROGRAM_POCS'] is not None and 'TITLE' in items['PROGRAM_POCS'][0] else 'NONE')
                                        feature.SetField("POCSPHONE", items['PROGRAM_POCS'][0]['PHONE'] if items['PROGRAM_POCS'] is not None and 'PHONE' in items['PROGRAM_POCS'][0] else 'NONE')
                                        feature.SetField("POCSTYPE", items['PROGRAM_POCS'][0]['POC_TYPE'] if items['PROGRAM_POCS'] is not None and 'POC_TYPE' in items['PROGRAM_POCS'][0] else 'NONE')

                                        geojson = {'type': 'Polygon', 'coordinates': polys}
                                        #create geometry from geojson
                                        polygon = ogr.CreateGeometryFromJson(str(geojson))
                                        feature.SetGeometry(polygon)
                                        layer.CreateFeature(feature)
                                        # Dereference the feature
                                        feature = None
                                elif geometry['type']=='GeometryCollection':
                                    #TODO handle Geometry Collection
                                    pass
                                elif geometry['type']=='LineString':
                                    #TODO handle LineString
                                    pass
                                else:
                                    print(geometry['type'] + " geometry type for " + str(items['PROGRAM_ID']))
                                # feature = None
                            else:
                                print("No ILF service area geometry for ILF ID: " + str(items['PROGRAM_ID']))   
            except Exception as e:
                print("Could not create ILF service area for ID: " + str(IDs))
                import sys
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("Line Number and Error: " + str(line) + " " + str(e))
        # Save and close the data source
        data_source = None
        return "Done creating ILF service areas."
    except Exception as e:
        print("Could not create ILF service area shapefile: " + str(IDs))
        import sys
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print("Line Number and Error: " + str(line) + " " + str(e))

#This function creates a point and polgyon from Ribits ILF mitigation site geojson webservice
def createilfsitesshp(path):
    try:
        import json
        import urllib3
        import arcpy
        import os
        # create a pool manager
        http = urllib3.PoolManager()
        #disable HTTPS SSL warning
        urllib3.disable_warnings()
        # get all current ILF program ids 
        program = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_list/')
        #load the response into json
        programdata = json.loads(program.data)
        # set up the shapefile driver
        driver = ogr.GetDriverByName("ESRI Shapefile")
        # create the data source
        data_source = driver.CreateDataSource(path)
        # create the spatial reference, WGS84
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        # create the polygon layer
        layer = data_source.CreateLayer("ILFFootprints", srs, geom_type=ogr.wkbPolygon)
        # create the centroid layer
        player = data_source.CreateLayer("ILFCentroids", srs, geom_type=ogr.wkbPoint)
        # Add the fields 
        layer.CreateField(ogr.FieldDefn("BANKNAME", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("CHAIR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("DISTRICT", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("OFFICE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("NOAAREGION", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("STATES", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("COUNTYS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("PERMITNUM", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("YEAREST", ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn("TOTALACRES", ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn("BANKSTATUS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("STATUSDATE", ogr.OFTDate))
        layer.CreateField(ogr.FieldDefn("BANKTYPE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("COMMENTS", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("RIBITSURL", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SERVAREA", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("SPONSOR", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("MNGRPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSFIRST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSLAST", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTITLE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSPHONE", ogr.OFTString))
        layer.CreateField(ogr.FieldDefn("POCSTYPE", ogr.OFTString))
        # add fields to centroid layer
        player.CreateField(ogr.FieldDefn("BANKNAME", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("CHAIR", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("DISTRICT", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("OFFICE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("NOAAREGION", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("STATES", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("COUNTYS", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("PERMITNUM", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("YEAREST", ogr.OFTInteger))
        player.CreateField(ogr.FieldDefn("TOTALACRES", ogr.OFTReal))
        player.CreateField(ogr.FieldDefn("BANKSTATUS", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("STATUSDATE", ogr.OFTDate))
        player.CreateField(ogr.FieldDefn("BANKTYPE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("COMMENTS", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("RIBITSURL", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("SERVAREA", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("SPONSOR", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRFIRST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRLAST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRTITLE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("MNGRPHONE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSFIRST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSLAST", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSTITLE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSPHONE", ogr.OFTString))
        player.CreateField(ogr.FieldDefn("POCSTYPE", ogr.OFTString))
        # create a dictionary of program IDs
        ilfprogramIDs = []
        # Add all the IDs to the dictionary
        for items in programdata['ITEMS']:
            # if items['PROGRAM_ID'] == 1382:
                ilfprogramIDs.append(items['PROGRAM_ID'])
            # for each program, get the program data
        for IDs in ilfprogramIDs:
            try:
                params = {"q": "{\"program_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
                # sed the get request for each id
                r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/ilf_program_data/', fields=params)
                data = r.data
                sitedata = json.loads(data)
                # create a dictionary of ILF site IDs
                ilfsiteIDs = []
                # Add all the ILF site IDs to the dictionary
                for sites in sitedata['ITEMS']:
                    if sites['PROGRAM_SITES']:
                        for bankids in sites['PROGRAM_SITES']:
                            #test code
                            # if bankids['BANK_ID'] ==3628:
                                ilfsiteIDs.append(bankids['BANK_ID'])
                # for each program, get the program data
                for IDs in ilfsiteIDs:
                    try:
                        params = {"q": "{\"bank_id\":" + str(IDs) + ",\"show_service_area\":\"Yes\"" + ",\"show_footprint\":\"Yes\"" + ",\"show_contacts\":\"Yes\"}"}
                        # send the get request for each id
                        r = http.request('GET', 'https://ribits.ops.usace.army.mil/ords/RI/public/bank_site_data/', fields=params)
                        data = r.data
                        bankdata = json.loads(data)
                        for items in bankdata['ITEMS']:
                            #create point feature if centroid is present
                            if 'BANK_LOCATION_CENTROID' in items:
                                # print("Centroid!")
                                # print(items['BANK_LOCATION_CENTROID'])
                                geometry = json.loads(items['BANK_LOCATION_CENTROID'])
                                feature = ogr.Feature(player.GetLayerDefn())
                                #set field values
                                feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                                feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                                feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                                feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                                feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                                feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                                feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                                feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                                feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                                feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                                feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                                geojson = {'type': 'Point', 'coordinates': geometry['coordinates']}
                                
                                point = ogr.CreateGeometryFromJson(str(geojson))
                                feature.SetGeometry(point)
                                player.CreateFeature(feature)
                                # Dereference the feature
                                feature = None
                                    
                            #make sure bank footprint is not null
                            if 'BANK_FOOTPRINT' in items:
                                #loop through all service areas (primary, secondary, etc.) and add the polygon to the feature class
                                for areas in items['BANK_FOOTPRINT']:
                                    #if geometry exsists then proceed
                                    if 'GEOM' in areas.keys() and areas['GEOM'] != 'null':
                                        #load geometry as json
                                        geometry = json.loads(areas['GEOM'])
                                        if geometry['type']=='Polygon':
                                            # pass
                                        #create geometry
                                        #initiate feature
                                            feature = ogr.Feature(layer.GetLayerDefn())
                                            #set field values
                                            feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                                            feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                            feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                            feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                            feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                            feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                            feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                            feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                            feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                            feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                            feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                                            feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                                            feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                                            feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                            feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                                            feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                            feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                                            feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                            feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                            feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                                            feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                                            feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                            feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                            feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                                            feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                                            feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                                            geojson = {'type': 'Polygon', 'coordinates': geometry['coordinates']}
                                            
                                            polygon = ogr.CreateGeometryFromJson(str(geojson))
                                            feature.SetGeometry(polygon)
                                            layer.CreateFeature(feature)
                                            # Dereference the feature
                                            feature = None
                                        #multipolygon handler
                                        elif geometry['type']=='MultiPolygon':
                                            
                                            for polys in geometry['coordinates']:
                                                #create geojson for each polygon
                                                #initiate feature
                                                feature = ogr.Feature(layer.GetLayerDefn())
                                                #set field values
                                                feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items and items['BANK_NAME'] is not None else 'NONE')
                                                feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items and items['CHAIR'] is not None else 'NONE')
                                                feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items and items['DISTRICT'] is not None else 'NONE')
                                                feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items and items['FIELD_OFFICE'] is not None else 'NONE')
                                                feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items and items['NOAA_FISHERIES_REGION'] is not None else 'NONE')
                                                feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items and items['STATE_LIST'] is not None else 'NONE')
                                                feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items and items['COUNTY_LIST'] is not None else 'NONE')
                                                feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items and items['PERMIT_NUMBER'] is not None else 'NONE')
                                                feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items and items['YEAR_ESTABLISHED'] is not None else 0)
                                                feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items and items['TOTAL_ACRES'] is not None else 0)
                                                feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items and items['BANK_STATUS'] is not None else 'NONE')
                                                feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items and items['BANK_STATUS_DATE'] is not None else '1/1/1700')
                                                feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items and items['BANK_TYPE'] is not None else 'NONE')
                                                feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items and items['COMMENTS'] is not None else 'NONE')
                                                feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items and items['RIBITS_URL_TO_BANK'] is not None else 'NONE')
                                                feature.SetField("SERVAREA", items['SERVICE_AREAS'][0]['SERVICE_AREA_NAME'] if items['SERVICE_AREAS'] is not None and 'SERVICE_AREA_NAME' in items['SERVICE_AREAS'][0] else 'NONE')
                                                feature.SetField("SPONSOR", items['BANK_SPONSORS'][0]['SPONSOR_NAME'] if items['BANK_SPONSORS'] is not None and 'SPONSOR_NAME' in items['BANK_SPONSORS'][0] else 'NONE')
                                                feature.SetField("MNGRFIRST", items['BANK_MANAGERS'][0]['FIRST_NAME'] if items['BANK_MANAGERS'] is not None and 'FIRST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                                feature.SetField("MNGRLAST", items['BANK_MANAGERS'][0]['LAST_NAME'] if items['BANK_MANAGERS'] is not None and 'LAST_NAME' in items['BANK_MANAGERS'][0] else 'NONE')
                                                feature.SetField("MNGRTITLE", items['BANK_MANAGERS'][0]['TITLE'] if items['BANK_MANAGERS'] is not None and 'TITLE' in items['BANK_MANAGERS'][0] else 'NONE')
                                                feature.SetField("MNGRPHONE", items['BANK_MANAGERS'][0]['PHONE'] if items['BANK_MANAGERS'] is not None and 'PHONE' in items['BANK_MANAGERS'][0] else 'NONE')
                                                feature.SetField("POCSFIRST", items['BANK_POCS'][0]['FIRST_NAME'] if items['BANK_POCS'] is not None and 'FIRST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                                feature.SetField("POCSLAST", items['BANK_POCS'][0]['LAST_NAME'] if items['BANK_POCS'] is not None and 'LAST_NAME' in items['BANK_POCS'][0] else 'NONE')
                                                feature.SetField("POCSTITLE", items['BANK_POCS'][0]['TITLE'] if items['BANK_POCS'] is not None and 'TITLE' in items['BANK_POCS'][0] else 'NONE')
                                                feature.SetField("POCSPHONE", items['BANK_POCS'][0]['PHONE'] if items['BANK_POCS'] is not None and 'PHONE' in items['BANK_POCS'][0] else 'NONE')
                                                feature.SetField("POCSTYPE", items['BANK_POCS'][0]['POC_TYPE'] if items['BANK_POCS'] is not None and 'POC_TYPE' in items['BANK_POCS'][0] else 'NONE')

                                                geojson = {'type': 'Polygon', 'coordinates': polys}
                                                #create geometry from geojson
                                                polygon = ogr.CreateGeometryFromJson(str(geojson))
                                                feature.SetGeometry(polygon)
                                                layer.CreateFeature(feature)
                                                # Dereference the feature
                                                feature = None
                                        elif geometry['type']=='GeometryCollection':
                                            #TODO handle Geometry Collection
                                            pass
                                        elif geometry['type']=='LineString':
                                            #TODO handle LineString
                                            pass
                                        else:
                                            print(geometry['type'] + " geometry type for " + str(items['BANK_ID']))
                                        # feature = None     
                    except Exception as e:
                        print("Could not create ILF footprint geometry! Bank ID: " + str(items['BANK_ID']))
                        import sys
                        trace_back = sys.exc_info()[2]
                        line = trace_back.tb_lineno
                        print("Line Number and Error: " + str(line) + " " + str(e))
            except Exception as e:
                print("Could not get ILF site footprint!")
                import sys
                trace_back = sys.exc_info()[2]
                line = trace_back.tb_lineno
                print("Line Number and Error: " + str(line) + " " + str(e))
    except Exception as e:
        print("Could not get ILF site footprint shapefile!")
        import sys
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print("Line Number and Error: " + str(line) + " " + str(e))

createbanksashp(r'C:\Users\k7rgrdls\Downloads\BankServiceAreas.shp')
createbanksitesshp(r'C:\Users\k7rgrdls\Downloads\BankFootprints.shp')
createilfprogsashp(r'C:\Users\k7rgrdls\Downloads\ILFServiceAreas.shp')
createilfsitesshp(r'C:\Users\k7rgrdls\Downloads\ILFFootprints.shp')

#TODO zip all shapefiles

#TODO Upload to CWBI Portal
