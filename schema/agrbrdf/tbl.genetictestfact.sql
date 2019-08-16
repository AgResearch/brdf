--
-- Name: genetictestfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genetictestfact (
    labresourceob integer NOT NULL,
    accession character varying(256),
    testtype character varying(1024),
    locusname character varying(256),
    variation character varying(1024),
    testdescription character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 305))
)
INHERITS (op);


ALTER TABLE public.genetictestfact OWNER TO agrbrdf;

