--
-- Name: gene_info; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gene_info (
    tax_id integer,
    geneid character varying(128),
    symbol character varying(64),
    locustag character varying(64),
    synonyms character varying(1024),
    dbxrefs character varying(1024),
    chromosome character varying(32),
    map_location character varying(64),
    description text,
    type_of_gene character varying(64),
    symbol_from_nomenclature_authority character varying(128),
    full_name_from_nomenclature_authority character varying(4196),
    nomenclature_status character varying(128),
    other_designations character varying(8192),
    modification_date character varying(16),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.gene_info OWNER TO agrbrdf;

