--
-- Name: sheepv3_prot_annotation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sheepv3_prot_annotation (
    seqid character varying(20),
    source character varying(10),
    type character varying(10),
    start integer,
    stop integer,
    score character varying(10),
    strand character varying(10),
    phase character varying(10),
    gene_model character varying(120),
    interproscan character varying(100),
    interproscan_go character varying(210),
    kegg character varying(470),
    swissprot character varying(160),
    datasourceob integer,
    voptypeid integer,
    seqname character varying(50)
);


ALTER TABLE public.sheepv3_prot_annotation OWNER TO agrbrdf;

