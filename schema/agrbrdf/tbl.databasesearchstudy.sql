--
-- Name: databasesearchstudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE databasesearchstudy (
    biodatabaseob integer,
    bioprotocolob integer,
    runby character varying(256),
    rundate date,
    studycomment character varying(2048),
    studytype character varying(128),
    studydescription character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 320))
)
INHERITS (op);


ALTER TABLE public.databasesearchstudy OWNER TO agrbrdf;

