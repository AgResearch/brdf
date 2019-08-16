--
-- Name: workflowstageob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowstageob (
    workflowstagename character varying(256),
    workflowstagetype character varying(64),
    workflowstagedescription character varying(2048),
    workflowstagecomment text,
    CONSTRAINT workflowstageob_workflowstagecomment CHECK ((obtypeid = 210))
)
INHERITS (ob);


ALTER TABLE public.workflowstageob OWNER TO agrbrdf;

