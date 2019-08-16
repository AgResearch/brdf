--
-- Name: geneticfunctionfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticfunctionfact (
    geneticob integer NOT NULL,
    goterm character varying(2048),
    godescription character varying(2048),
    functiondescription character varying(2048),
    functioncomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 190))
)
INHERITS (op);


ALTER TABLE public.geneticfunctionfact OWNER TO agrbrdf;

