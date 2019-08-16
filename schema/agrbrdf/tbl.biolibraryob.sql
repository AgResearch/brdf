--
-- Name: biolibraryob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biolibraryob (
    libraryname character varying(1024),
    librarytype character varying(256),
    librarydate date,
    librarydescription text,
    librarystorage text,
    CONSTRAINT biolibraryob_obtypeid_check CHECK ((obtypeid = 485))
)
INHERITS (ob);


ALTER TABLE public.biolibraryob OWNER TO agrbrdf;

