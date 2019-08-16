--
-- Name: displayfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE displayfunction (
    ob integer NOT NULL,
    datasourceob integer,
    displayprocedureob integer NOT NULL,
    functioncomment character varying(1024),
    invocation text,
    invocationorder integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 145))
)
INHERITS (op);


ALTER TABLE public.displayfunction OWNER TO agrbrdf;

