import postgres
import requests
import string
import json
from datetime import datetime
import base64


def getInsertValue(value):
    returnVal = ''
    if (value == None):
        returnVal = None
    elif (isNumber(value)):
        returnVal = value
    else:
        returnVal = value

    return returnVal


def insertFeature(row, feature):
    type = row['type'].encode('utf-8')
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

    name = feature['properties'][nameField].encode('utf-8').title()
    muni = feature['properties'][muniField].encode('utf-8').title()
    locationString = name + "|" + type + "|" + muni
    locationId = base64.b64encode(locationString)

    if (aliasField == None):
        alias = None
    else:
        if feature['properties'][aliasField] != None:
            alias = feature['properties'][aliasField].encode('utf-8').title()
        else:
            alias = None

    insertSqlTemplate = """ INSERT INTO public.tbl_search (\"name\", alias, \"type\", type_id, municipality,geojson,geojson_extent,geojson_point, location_id,priority) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    # print(name)
    # print(alias)
    # print(type)
    # print(muni)
    values = (getInsertValue(name), getInsertValue(alias),
              getInsertValue(type), typeId, getInsertValue(muni), geometryGeojson, extentGeojson, pointGeojson, locationId, priority)
    return postgres.executeNonQuery(
        connTabular, insertSqlTemplate, values)


def isNumber(value):
    try:
        int(value)
        return True
    except:
        return False


connTabular = postgres.getConn('tabular')
connWeblive = postgres.getConn('weblive')

# DROP INDEX
postgres.executeNonQuery(connTabular, "DROP INDEX tbl_search_trgm_idx_name;")
postgres.executeNonQuery(connTabular, "DROP INDEX tbl_search_trgm_idx_alias;")
postgres.executeNonQuery(
    connTabular, "DROP INDEX tbl_search_trgm_idx_priority;")

rows = postgres.query(connTabular, 'SELECT id, "type", type_id, field_name, field_name_alias, muni_field_name, roll_number_field, run_schedule, priority, last_run, last_run_minutes,wfs_url FROM public.tbl_search_layers;')
for row in rows:
    # GET START TIME
    startTime = datetime.now()

    # GET VALUES
    type = row['type']
    typeId = row['type_id']
    nameField = row['field_name']
    muniField = row['muni_field_name']
    aliasField = row['field_name_alias']
    wfsUrl = row['wfs_url']
    runSchedule = row['run_schedule']

    if (runSchedule == None):
        continue

    print("Processing: " + type + " " + typeId)

    typeId2 = (typeId)
    postgres.executeNonQuery(
        connTabular, """delete from public.tbl_search where type_id = %s""", (typeId,))

    r = requests.get(url=wfsUrl, verify=False)

    # extracting data in json format
    data = r.json()
    features = data['features']
    for feature in features:
        queryOk = insertFeature(row, feature)
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
                         "CREATE INDEX tbl_search_trgm_idx_alias ON public.tbl_search USING gin (name gin_trgm_ops);")
postgres.executeNonQuery(connTabular,
                         "CREATE INDEX tbl_search_trgm_idx_priority ON public.tbl_search USING gin (name gin_trgm_ops);")

connTabular.close()
connWeblive.close()

print("COMPLETE!")
