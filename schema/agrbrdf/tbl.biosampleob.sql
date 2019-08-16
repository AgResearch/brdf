--
-- Name: biosampleob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosampleob (
    samplename character varying(1024),
    sampletype character varying(256),
    sampletissue character varying(256),
    sampledate date,
    sampledescription text,
    samplestorage text,
    samplecount double precision,
    samplecountunit character varying(64),
    sampleweight double precision,
    sampleweightunit character varying(64),
    samplevolume double precision,
    samplevolumeunit character varying(64),
    sampledrymatterequiv double precision,
    sampledmeunit character varying(64),
    CONSTRAINT "$1" CHECK ((obtypeid = 90))
)
INHERITS (ob);


ALTER TABLE public.biosampleob OWNER TO agrbrdf;

