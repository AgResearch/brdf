--
-- Name: geneticfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticfact (
    geneticob integer NOT NULL,
    factnamespace character varying(256),
    attributename character varying(256),
    attributevalue character varying(4096),
    CONSTRAINT "$1" CHECK ((obtypeid = 200))
)
INHERITS (op);


ALTER TABLE public.geneticfact OWNER TO agrbrdf;

