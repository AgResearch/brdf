--
-- Name: genotypes; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypes (
    sample_id character varying(32),
    snp_name character varying(64),
    allele1_forward character varying(10),
    allele2_forward character varying(10),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.genotypes OWNER TO agrbrdf;

