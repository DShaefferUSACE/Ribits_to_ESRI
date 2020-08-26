from osgeo import gdal
from osgeo import ogr
from osgeo import osr

def createbanksafc():
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
    data_source = driver.CreateDataSource(r'C:\Users\k7rgrdls\Downloads\BankServiceAreas.shp')
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
        # if items['BANK_ID'] == 777:
        # if items['BANK_ID'] == 11 or items['BANK_ID'] == 777:
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
                    #loop through all service areas (primary, secondary, etc.) and add the polygon to the feature class
                    for areas in items['SERVICE_AREAS']:
                        #if geometry exsists then proceed
                        if 'GEOM' in areas.keys():
                            #initiate feature
                            feature = ogr.Feature(layer.GetLayerDefn())
                            #set field values
                            feature.SetField("BANKNAME", items['BANK_NAME'] if 'BANK_NAME' in items else 'NONE')
                            feature.SetField("CHAIR", items['CHAIR'] if 'CHAIR' in items else 'NONE')
                            feature.SetField("DISTRICT", items['DISTRICT'] if 'DISTRICT' in items  else 'NONE')
                            feature.SetField("OFFICE", items['FIELD_OFFICE'] if 'FIELD_OFFICE' in items else 'NONE')
                            feature.SetField("NOAAREGION", items['NOAA_FISHERIES_REGION'] if 'NOAA_FISHERIES_REGION' in items else 'NONE')
                            feature.SetField("STATES", items['STATE_LIST'] if 'STATE_LIST' in items else 'NONE')
                            feature.SetField("COUNTYS", items['COUNTY_LIST'] if 'COUNTY_LIST' in items else 'NONE')
                            feature.SetField("PERMITNUM", items['PERMIT_NUMBER'] if 'PERMIT_NUMBER' in items else 'NONE')
                            feature.SetField("YEAREST", items['YEAR_ESTABLISHED'] if 'YEAR_ESTABLISHED' in items else 0)
                            feature.SetField("TOTALACRES", items['TOTAL_ACRES'] if 'TOTAL_ACRES' in items else 0)
                            feature.SetField("BANKSTATUS", items['BANK_STATUS'] if 'BANK_STATUS' in items else 'NONE')
                            feature.SetField("STATUSDATE", items['BANK_STATUS_DATE'] if 'BANK_STATUS_DATE' in items else '1/1/1700')
                            feature.SetField("BANKTYPE", items['BANK_TYPE'] if 'BANK_TYPE' in items else 'NONE')
                            feature.SetField("COMMENTS", items['COMMENTS'] if 'COMMENTS' in items else 'NONE')
                            feature.SetField("RIBITSURL", items['RIBITS_URL_TO_BANK'] if 'RIBITS_URL_TO_BANK' in items else 'NONE')
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
                            #load geometry as json
                            geometry = json.loads(areas['GEOM'])
                         #handle the various geometry types
                            if geometry['type']=='Polygon':
                               #create geometry
                                polygon = ogr.CreateGeometryFromJson(str(geometry))
                                feature.SetGeometry(polygon)
                                layer.CreateFeature(feature)
                                # Dereference the feature
                                # feature = None
                            #multipolygon handler
                            elif geometry['type']=='MultiPolygon':
                                for polys in geometry['coordinates']:
                                    #create geojson for each polygon
                                    geojson = {'type': 'Polygon', 'coordinates': polys}
                                    #create geometry from geojson
                                    polygon = ogr.CreateGeometryFromJson(str(geojson))
                                    feature.SetGeometry(polygon)
                                    layer.CreateFeature(feature)
                                    # Dereference the feature

                            elif geometry['type']=='GeometryCollection':
                                #TODO handle Geometry Collection
                                pass
                            elif geometry['type']=='LineString':
                                #TODO handle LineString
                                pass
                            else:
                                print(geometry['type'] + " geometry type for " + str(items['BANK_ID']))
                            feature = None
                        else:
                            print("No bank service area geometry for bank ID: " + str(items['BANK_ID']))   
        except Exception as e:
            print(e)
            print("Could not create bank service area for ID: " + str(IDs))
    # Save and close the data source
    data_source = None


createbanksafc()