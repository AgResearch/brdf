--
-- Name: blastn_results; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE blastn_results (
    runname character varying(30),
    querylength integer,
    queryid character varying(256),
    queryidindex character varying(256),
    hitid character varying(256),
    strand character varying(20),
    hitlength integer,
    description text,
    score double precision,
    evalue double precision,
    alignidentities integer,
    alignoverlaps integer,
    alignmismatches integer,
    aligngaps integer,
    qstart integer,
    qstop integer,
    hstart integer,
    hstop integer,
    keywords character varying(10),
    pctidentity double precision,
    species character varying(30),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.blastn_results OWNER TO agrbrdf;

