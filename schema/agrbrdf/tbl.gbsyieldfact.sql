--
-- Name: gbsyieldfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE gbsyieldfact (
    factid integer DEFAULT nextval('gbsyf_factidseq'::regclass) NOT NULL,
    biosamplelist integer NOT NULL,
    biosampleob integer,
    sqname character varying(32),
    sampleid character varying(64),
    flowcell character varying(32),
    lane integer,
    sqnumber integer,
    tag_count integer,
    read_count integer,
    callrate double precision,
    sampdepth double precision,
    cohort character varying(128)
);


ALTER TABLE public.gbsyieldfact OWNER TO agrbrdf;

