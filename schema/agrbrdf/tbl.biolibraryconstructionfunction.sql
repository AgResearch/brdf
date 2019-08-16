--
-- Name: biolibraryconstructionfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biolibraryconstructionfunction (
    biosampleob integer NOT NULL,
    biolibraryob integer NOT NULL,
    bioprotocolob integer,
    labresourcelist integer,
    labresourceob integer,
    labbookreference character varying(2048),
    constructioncomment character varying(1024),
    constructiondate date,
    CONSTRAINT biolibraryconstructionfunction_obtypeid_check CHECK ((obtypeid = 495))
)
INHERITS (op);


ALTER TABLE public.biolibraryconstructionfunction OWNER TO agrbrdf;

