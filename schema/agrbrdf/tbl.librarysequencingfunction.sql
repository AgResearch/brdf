--
-- Name: librarysequencingfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE librarysequencingfunction (
    biolibraryob integer,
    datasourceob integer NOT NULL,
    bioprotocolob integer,
    labresourcelist integer,
    labresourceob integer,
    runby character varying(256),
    rundate date,
    functioncomment character varying(1024),
    CONSTRAINT librarysequencingfunction_obtypeid_check CHECK ((obtypeid = 500))
)
INHERITS (op);


ALTER TABLE public.librarysequencingfunction OWNER TO agrbrdf;

