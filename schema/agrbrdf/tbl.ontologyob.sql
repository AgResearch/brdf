--
-- Name: ontologyob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ontologyob (
    ontologyname character varying(256) NOT NULL,
    ontologydescription character varying(1024),
    ontologycomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 5))
)
INHERITS (ob);


ALTER TABLE public.ontologyob OWNER TO agrbrdf;

