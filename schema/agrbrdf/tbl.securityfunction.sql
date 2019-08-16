--
-- Name: securityfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE securityfunction (
    ob integer,
    applytotype integer,
    securityprocedureob integer NOT NULL,
    functioncomment character varying(1024),
    invocation text,
    invocationorder integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 465))
)
INHERITS (op);


ALTER TABLE public.securityfunction OWNER TO agrbrdf;

