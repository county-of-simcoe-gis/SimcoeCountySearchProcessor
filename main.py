from re import split
import postgres
import requests
import string
import json
from datetime import datetime
import base64
import urllib.parse as urlparse
from urllib.parse import parse_qs
from xml.dom import minidom
import xml.etree.ElementTree as ET
import xmltodict

with open('config.json') as config_json:
    data = json.load(config_json)

fallbackMuniTable = data['fallbackMuniTable']


def getInsertValue(value):
    returnVal = ''
    if (value == None):
        returnVal = None
    elif (isNumber(value)):
        returnVal = value
    else:
        returnVal = value

    return returnVal


def insertFeature(row, feature,isOpenData):
    # itemType = row['type'].encode('utf-8').title()
    itemType = row['type']
    typeId = row['type_id']
    priority = row['priority']
    nameField = row['field_name']
    muniField = row['muni_field_name']
    aliasField = row['field_name_alias']
    geometryObj = feature['geometry']
    geometryType = geometryObj['type']
    geometryGeojson = json.dumps(geometryObj)

    extentSql = None
    pointSql = None
    if geometryType == "Point":
        # BUFFER BY 1 METER TO RETURN A VALID EXTENT
        extentSql = "SELECT ST_AsGeoJSON(ST_Extent(ST_Buffer(ST_GeomFromGeoJSON('{0}'), 1))) As geojson;"
        pointGeojson = geometryGeojson
    else:
        extentSql = "SELECT ST_AsGeoJSON(ST_Extent(ST_GeomFromGeoJSON('{0}'))) As geojson;"
        pointSql = "SELECT ST_AsGeoJSON(fn_sc_find_geometry_center(ST_SetSRID(ST_GeomFromGeoJSON('{0}'), 3857))) As geojson;"

    extentRow = postgres.queryOne(
        connWeblive, extentSql.format(geometryGeojson))
    extentGeojson = extentRow['geojson']

    if (pointSql != None):
        pointRow = postgres.queryOne(
            connWeblive, pointSql.format(geometryGeojson))
        pointGeojson = pointRow['geojson']

    # name = feature['properties'][nameField].encode('utf-8').title()
    # muni = feature['properties'][muniField].encode('utf-8').title()
    name = feature['properties'][nameField]
    if (name == None):
        return "OK"

    # SELECT muni FROM public.sc_simcoectyjurisdictions where ST_Intersects(geom, ST_SetSRID(ST_GeomFromGeoJSON('{"type": "Point", "coordinates": [-8929107.2899, 5543302.053]}'), 3857));
    # GET MUNI IF WE DON'T HAVE ONE
    if (muniField == None and fallbackMuniTable != ""):
        muniSql = "SELECT muni FROM {0} where ST_Intersects(geom, ST_SetSRID(ST_GeomFromGeoJSON('{1}'), 3857));"
        muniRow = postgres.queryOne(
            connWeblive, muniSql.format(fallbackMuniTable, pointGeojson))
        if (muniRow == None):
            muni = ''
        else:
            muni = muniRow['muni']
            if (muni == None):
                muni = ''
    else:
        if (muniField == None):
            muni = ''
        else:
            muni = feature['properties'][muniField]
            if (muni == None):
                muni = ''

    locationString = name + \
        "|" + itemType + \
        "|" + muni
    #locationId = base64.b64encode(locationString.encode('utf-8').title())
    locationIdBytes = base64.b64encode(locationString.encode('utf-8'))
    locationId = str(locationIdBytes, "utf-8")
    if (aliasField == None):
        alias = None
    else:
        if feature['properties'][aliasField] != None:
            alias = feature['properties'][aliasField]
        else:
            alias = None

    insertSqlTemplate = """ INSERT INTO public.tbl_search (\"name\", alias, \"type\", type_id, municipality,geojson,geojson_extent,geojson_point, location_id,priority, is_open_data) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    values = (getInsertValue(name), getInsertValue(alias),
              getInsertValue(itemType), typeId, getInsertValue(muni), geometryGeojson, extentGeojson, pointGeojson, locationId, priority, isOpenData)
    a = postgres.executeNonQuery(connTabular, insertSqlTemplate, values)
    return a


def isNumber(value):
    try:
        int(value)
        return True
    except:
        return False


def dropIndex(conn, command):
    try:
        postgres.executeNonQuery(connTabular, command)
        return True
    except:
        return False

def isOpenData(wfsUrl):
    try:
        urlParsed = urlparse.urlparse(wfsUrl)
        names = parse_qs(urlParsed.query)['typeNames'][0].split(":")
        workspace = names[0]
        name = names[1]
        infoUrlTemplate = "https://opengis.simcoe.ca/geoserver/{0}/{1}/ows?service=wms&version=1.3.0&request=GetCapabilities"
        infoUrl = infoUrlTemplate.format(workspace, name)
        xmlResponse = requests.get(infoUrl).content
        doc = xmltodict.parse(xmlResponse)
        keywords = doc['WMS_Capabilities']['Capability']['Layer']['Layer']['KeywordList']['Keyword']
        if "DOWNLOAD" in keywords:
            return True
        else:
            return False
    except:
        return False

connTabular = postgres.getConn('tabular')
connWeblive = postgres.getConn('weblive')

# DROP INDEX
dropIndex(connTabular, "DROP INDEX IF EXISTS tbl_search_trgm_idx_name;")
dropIndex(connTabular, "DROP INDEX IF EXISTS tbl_search_trgm_idx_alias;")
dropIndex(connTabular, "DROP INDEX IF EXISTS tbl_search_trgm_idx_priority;")

rows = postgres.query(connTabular, 'SELECT id, "type", type_id, field_name, field_name_alias, muni_field_name, roll_number_field, run_schedule, priority, last_run, last_run_minutes,wfs_url FROM public.tbl_search_layers order by type;')
for row in rows:
    # GET START TIME
    startTime = datetime.now()

    # GET VALUES
    itemType = row['type']
    typeId = row['type_id']
    nameField = row['field_name']
    muniField = row['muni_field_name']
    aliasField = row['field_name_alias']
    wfsUrl = row['wfs_url']
    runSchedule = row['run_schedule']

    isOpenDataVar = isOpenData(wfsUrl)
    if (runSchedule != 'ALWAYS'):
    # if (runSchedule != 'ONETIME'):
        continue

    print("Processing: " + itemType + " " + typeId)

    typeId2 = (typeId)
    postgres.executeNonQuery(
        connTabular, """delete from public.tbl_search where type_id = %s""", (typeId,))

    r = requests.get(url=wfsUrl, verify=False)

    # extracting data in json format
    data = r.json()
    features = data['features']
    for feature in features:
        queryOk = insertFeature(row, feature, isOpenDataVar)
        if (queryOk != "OK"):
            print("Layer Type Id Failed: " + typeId)

    endTime = datetime.now()
    minutes = (endTime - startTime).total_seconds() / 60
    print(typeId + " took: " + str(minutes) + " minutes")

    updateQuery = "UPDATE public.tbl_search_layers SET last_run = %s, last_run_minutes = %s where type_id = %s"
    updateValues = (datetime.now(), minutes, typeId)
    postgres.executeNonQuery(
        connTabular, updateQuery, updateValues)

# REINDEX TABLE
postgres.executeNonQuery(connTabular,
                         "CREATE INDEX tbl_search_trgm_idx_name ON public.tbl_search USING gin (name gin_trgm_ops);")
postgres.executeNonQuery(connTabular,
                         "CREATE INDEX tbl_search_trgm_idx_alias ON public.tbl_search USING gin (alias gin_trgm_ops);")
postgres.executeNonQuery(connTabular,
                         "CREATE INDEX tbl_search_trgm_idx_priority ON public.tbl_search USING gin (priority gin_trgm_ops);")

connTabular.close()
connWeblive.close()

print("COMPLETE!")
