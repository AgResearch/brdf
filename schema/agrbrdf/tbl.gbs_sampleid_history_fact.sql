--
-- Name: gbs_sampleid_history_fact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbs_sampleid_history_fact (
    biosampleob integer NOT NULL,
    sample character varying(32),
    qc_sampleid character varying(32),
    comment character varying(256),
    createddate date DEFAULT now(),
    createdby character varying(256),
    voptypeid integer
);


ALTER TABLE public.gbs_sampleid_history_fact OWNER TO agrbrdf;

