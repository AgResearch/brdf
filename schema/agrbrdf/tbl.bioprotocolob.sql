--
-- Name: bioprotocolob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE bioprotocolob (
    protocolname character varying(1024),
    protocoltype character varying(1024),
    protocoldescription character varying(1024),
    protocoltext text,
    CONSTRAINT "$1" CHECK ((obtypeid = 95))
)
INHERITS (ob);


ALTER TABLE public.bioprotocolob OWNER TO agrbrdf;

