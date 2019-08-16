--
-- Name: samplesheet_temp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE samplesheet_temp (
    fcid character varying(32),
    lane integer,
    sampleid character varying(32),
    sampleref character varying(32),
    sampleindex character varying(1024),
    description character varying(256),
    control character varying(32),
    recipe integer,
    operator character varying(256),
    sampleproject character varying(256),
    sampleplate character varying(64),
    samplewell character varying(64),
    downstream_processing character varying(64),
    basespace_project character varying(256)
);


ALTER TABLE public.samplesheet_temp OWNER TO agrbrdf;

