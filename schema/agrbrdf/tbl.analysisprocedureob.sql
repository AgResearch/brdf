--
-- Name: analysisprocedureob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE analysisprocedureob (
    procedurename character varying(1024),
    author character varying(2048),
    authordate date,
    sourcecode text,
    proceduredescription character varying(1024),
    procedurecomment text,
    proceduretype character varying(64),
    invocation text,
    presentationtemplate text,
    textincount integer,
    textoutcount integer,
    imageoutcount integer,
    CONSTRAINT analysisprocedureob_obtypeid_check CHECK ((obtypeid = 540))
)
INHERITS (ob);


ALTER TABLE public.analysisprocedureob OWNER TO agrbrdf;

