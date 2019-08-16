--
-- Name: genotypestudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypestudy (
    biosamplelist integer,
    biosampleob integer,
    labresourcelist integer,
    labresourceob integer,
    bioprotocolob integer NOT NULL,
    studytype character varying(128),
    CONSTRAINT "$1" CHECK ((obtypeid = 290))
)
INHERITS (op);


ALTER TABLE public.genotypestudy OWNER TO agrbrdf;

