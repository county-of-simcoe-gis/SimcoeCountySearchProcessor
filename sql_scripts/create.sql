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
