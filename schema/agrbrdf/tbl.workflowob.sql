--
-- Name: workflowob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowob (
    workflowname character varying(256),
    workflowdescription character varying(2048),
    workflowcomment text,
    CONSTRAINT workflowob_workflowcomment CHECK ((obtypeid = 205))
)
INHERITS (ob);


ALTER TABLE public.workflowob OWNER TO agrbrdf;

