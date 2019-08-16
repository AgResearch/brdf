--
-- Name: biosubjectob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosubjectob (
    subjectname character varying(1024),
    subjectspeciesname character varying(1024),
    subjecttaxon integer,
    strain character varying(1024),
    subjectdescription text,
    dob date,
    sex character varying(5),
    CONSTRAINT "$2" CHECK ((obtypeid = 85))
)
INHERITS (ob);


ALTER TABLE public.biosubjectob OWNER TO agrbrdf;

