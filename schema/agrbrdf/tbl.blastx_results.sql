--
-- Name: blastx_results; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE blastx_results (
    runname character varying(30),
    querylength integer,
    queryid character varying(128),
    hitid character varying(30),
    frame integer,
    hitlength integer,
    description text,
    score double precision,
    evalue double precision,
    alignidentities integer,
    alignoverlaps integer,
    alignpositives integer,
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


ALTER TABLE public.blastx_results OWNER TO agrbrdf;

