--
-- Name: securityprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE securityprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    proceduredescription character varying(1024),
    procedurecomment text,
    invocation text,
    CONSTRAINT "$1" CHECK ((obtypeid = 460))
)
INHERITS (ob);


ALTER TABLE public.securityprocedureob OWNER TO agrbrdf;

