--
-- Name: displayprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE displayprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    procedurecomment text,
    invocation text,
    proceduredescription character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 140))
)
INHERITS (ob);


ALTER TABLE public.displayprocedureob OWNER TO agrbrdf;

