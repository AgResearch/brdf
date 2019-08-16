--
-- Name: geneticob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticob (
    geneticobname character varying(256),
    geneticobtype character varying(256),
    geneticobdescription text,
    geneticobsymbols character varying(2048),
    obcomment character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 160))
)
INHERITS (ob);


ALTER TABLE public.geneticob OWNER TO agrbrdf;

