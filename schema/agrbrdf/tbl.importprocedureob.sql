--
-- Name: importprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE importprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    procedurecomment text,
    importdatasourceinvocation text,
    displaydatasourceinvocation text,
    CONSTRAINT "$1" CHECK ((obtypeid = 130))
)
INHERITS (ob);


ALTER TABLE public.importprocedureob OWNER TO agrbrdf;

