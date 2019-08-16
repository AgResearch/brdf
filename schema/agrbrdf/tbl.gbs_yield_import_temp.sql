--
-- Name: gbs_yield_import_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbs_yield_import_temp (
    run character varying(64),
    sqname character varying(32),
    sampleid character varying(32),
    flowcell character varying(32),
    lane character varying(32),
    sqnumber character varying(32),
    tag_count character varying(32),
    read_count character varying(32),
    callrate character varying(32),
    sampdepth character varying(32),
    seqid character varying(64),
    matched integer,
    cohort character varying(128)
);


ALTER TABLE public.gbs_yield_import_temp OWNER TO agrbrdf;

--
-- Name: keyfile_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE keyfile_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.keyfile_factidseq OWNER TO agrbrdf;

