--
-- Name: print139annotationbackup2; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE print139annotationbackup2 (
    contentid character varying(128),
    estname character varying(128),
    contig character varying(128),
    libexpression character varying(5192),
    hs_mm_rn_nr_gene character varying(32),
    taxid character varying(32),
    symbol character varying(256),
    synonyms character varying(256),
    chromosome character varying(128),
    map_location character varying(64),
    description character varying(5192),
    type_of_gene character varying(64),
    dummy character varying(4),
    datasourceob integer,
    voptypeid integer,
    symbolaccession character varying(64),
    oarchromosome character varying(32)
);


ALTER TABLE public.print139annotationbackup2 OWNER TO agrbrdf;

