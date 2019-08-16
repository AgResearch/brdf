--
-- Name: hg18uniquereads; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE hg18uniquereads (
    uniquetype character varying(20),
    queryfrag character varying(64),
    mappedtofrag character varying(64),
    sequencedfrom character varying(32),
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.hg18uniquereads OWNER TO agrbrdf;

--
-- Name: samplesheet_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE samplesheet_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.samplesheet_factidseq OWNER TO agrbrdf;

