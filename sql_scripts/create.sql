CREATE EXTENSION pg_trgm;

CREATE TABLE public.tbl_search (
	id int4 NOT NULL GENERATED ALWAYS AS IDENTITY,
	"name" text NOT NULL,
	alias text NULL,
	"type" text NULL,
	municipality text NULL,
	type_id varchar NOT NULL,
	geojson text NULL,
	geojson_extent varchar NULL,
	location_id text NULL,
	priority int4 NULL,
	geojson_point varchar NULL,
	CONSTRAINT tbl_search_pk PRIMARY KEY (id)
);
CREATE INDEX tbl_search_trgm_idx_alias ON public.tbl_search USING gin (name gin_trgm_ops);
CREATE INDEX tbl_search_trgm_idx_name ON public.tbl_search USING gin (name gin_trgm_ops);
CREATE INDEX tbl_search_trgm_idx_priority ON public.tbl_search USING gin (name gin_trgm_ops);

CREATE TABLE public.tbl_search_layers (
	id serial NOT NULL,
	"type" varchar NULL,
	type_id varchar NULL,
	field_name varchar NULL,
	field_name_alias varchar NULL,
	muni_field_name varchar NULL,
	roll_number_field varchar NULL,
	run_schedule varchar NULL,
	priority varchar NULL,
	last_run varchar NULL,
	last_run_minutes float4 NULL,
	wfs_url text NOT NULL,
	CONSTRAINT tbl_search_layers_pkey PRIMARY KEY (id)
);

INSERT INTO public.tbl_search_layers ("type",type_id,field_name,field_name_alias,muni_field_name,roll_number_field,run_schedule,priority,last_run,last_run_minutes,wfs_url) VALUES 
('Airport','sc_airport','name',NULL,'muni',NULL,'ALWAYS','10','2019-09-25 08:41:59.844',0.009483334,'https://opengis.simcoe.ca/geoserver/wfs?service=wfs&version=2.0.0&request=GetFeature&typeNames=simcoe:Airport&outputFormat=application/json')
,('Police Station','sc_policestation','name',NULL,'muni',NULL,'ALWAYS','5','2019-09-25 08:42:00.268',0.0069333334,'https://opengis.simcoe.ca/geoserver/wfs?service=wfs&version=2.0.0&request=GetFeature&typeNames=simcoe:Police_Station&outputFormat=application/json')
,('Museum And Archives','sc_museumandarchives','name',NULL,'muni',NULL,'ALWAYS','5','2019-09-25 08:42:00.55',0.00465,'https://opengis.simcoe.ca/geoserver/wfs?service=wfs&version=2.0.0&request=GetFeature&typeNames=simcoe:Museum_and_Archives&outputFormat=application/json')
,('Hospital','sc_hospital','name',NULL,'muni',NULL,'ALWAYS','5','2019-09-25 08:58:45.324',0.011983333,'https://opengis.simcoe.ca/geoserver/wfs?service=wfs&version=2.0.0&request=GetFeature&typeNames=simcoe:Hospital&outputFormat=application/json')
;
