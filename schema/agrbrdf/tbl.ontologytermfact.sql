--
-- Name: ontologytermfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ontologytermfact (
    ontologyob integer NOT NULL,
    termname character varying(256),
    termdescription character varying(2048),
    unitname character varying(256),
    termcode character varying(16),
    CONSTRAINT "$1" CHECK ((obtypeid = 10))
)
INHERITS (op);


ALTER TABLE public.ontologytermfact OWNER TO agrbrdf;

