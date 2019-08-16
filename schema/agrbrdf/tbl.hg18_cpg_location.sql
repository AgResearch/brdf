--
-- Name: hg18_cpg_location; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18_cpg_location (
    chrom character varying(20),
    chromstart integer,
    chromend integer,
    name character varying(10),
    length integer,
    cpgnum integer,
    gcnum integer,
    percpg double precision,
    pergc double precision,
    obsexp double precision,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18_cpg_location OWNER TO agrbrdf;

