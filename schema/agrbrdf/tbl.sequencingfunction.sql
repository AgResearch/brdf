--
-- Name: sequencingfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sequencingfunction (
    biosampleob integer,
    biosequenceob integer NOT NULL,
    labresourcelist integer,
    labresourceob integer,
    sequencedby character varying(256),
    sequencingdate date,
    functioncomment character varying(1024),
    biolibraryob integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 120))
)
INHERITS (op);


ALTER TABLE public.sequencingfunction OWNER TO agrbrdf;

