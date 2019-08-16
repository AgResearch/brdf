--
-- Name: datasourceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourceob (
    datasourcename character varying(1024),
    datasourcetype character varying(256),
    datasupplier character varying(2048),
    physicalsourceuri character varying(2048),
    datasupplieddate date,
    datasourcecomment text,
    numberoffiles integer,
    datasourcecontent text,
    dynamiccontentmethod character varying(256),
    uploadsourceuri character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 125))
)
INHERITS (ob);


ALTER TABLE public.datasourceob OWNER TO agrbrdf;

