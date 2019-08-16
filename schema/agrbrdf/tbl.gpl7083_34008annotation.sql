--
-- Name: gpl7083_34008annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gpl7083_34008annotation (
    id integer,
    col integer,
    "row" integer,
    name character varying(20),
    spot_id character varying(20),
    control_type character varying(10),
    refseq character varying(20),
    gb_acc character varying(20),
    locuslink_id character varying(10),
    gene_symbol character varying(20),
    gene_name character varying(160),
    unigene_id character varying(10),
    ensembl_id character varying(20),
    tigr_id character varying(10),
    accession_string character varying(100),
    chromosomal_location character varying(10),
    cytoband character varying(10),
    description character varying(210),
    go_id character varying(3300),
    sequence character varying(70),
    datasourceob integer,
    voptypeid integer,
    human_refseqacc character varying(32),
    human_refseqevalue double precision,
    human_refseqdescription character varying(4096),
    human_refseqgenesymbol character varying(32),
    human_refseqgenedescription character varying(4096),
    ensbiomart_geneid integer,
    ensbiomart_genesymbol character varying(32),
    ensbiomart_genedescription character varying(4096),
    human_refseqgeneid integer
);


ALTER TABLE public.gpl7083_34008annotation OWNER TO agrbrdf;

