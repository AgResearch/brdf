--
-- Name: hg18_cpg_mspi_overlap; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_cpg_mspi_overlap (
    cpg_uniqueid character varying(30),
    chromstart integer,
    chromend integer,
    cpg_length integer,
    cpg_name character varying(10),
    frag_uniqueid character varying(30),
    start integer,
    stop integer,
    frag_length integer,
    datasourceob integer,
    voptypeid integer,
    chrom character varying(32)
);


ALTER TABLE public.hg18_cpg_mspi_overlap OWNER TO agrbrdf;

