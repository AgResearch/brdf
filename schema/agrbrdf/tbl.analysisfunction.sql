--
-- Name: analysisfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE analysisfunction (
    ob integer NOT NULL,
    datasourcelist integer,
    datasourcedescriptors text,
    analysisprocedureob integer NOT NULL,
    functioncomment character varying(1024),
    invocation text,
    invocationorder integer,
    datasourceob integer,
    CONSTRAINT analysisfunction_obtypeid_check CHECK ((obtypeid = 545))
)
INHERITS (op);


ALTER TABLE public.analysisfunction OWNER TO agrbrdf;

