--
-- Name: geneexpressionstudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneexpressionstudy (
    biosamplelist integer NOT NULL,
    labresourcelist integer,
    labresourceob integer,
    bioprotocolob integer,
    studytype character varying(128),
    studydescription text,
    studyname character varying(128),
    CONSTRAINT "$1" CHECK ((obtypeid = 240))
)
INHERITS (op);


ALTER TABLE public.geneexpressionstudy OWNER TO agrbrdf;

