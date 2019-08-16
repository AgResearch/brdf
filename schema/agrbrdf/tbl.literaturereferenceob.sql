--
-- Name: literaturereferenceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE literaturereferenceob (
    journalname character varying(2048) NOT NULL,
    volumename character varying(16),
    volnumber integer,
    voldate date,
    papertitle character varying(2048),
    authors character varying(4096),
    abstract text,
    ourcomments text,
    CONSTRAINT "$1" CHECK ((obtypeid = 60))
)
INHERITS (ob);


ALTER TABLE public.literaturereferenceob OWNER TO agrbrdf;

