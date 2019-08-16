--
-- Name: workstagevisitfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workstagevisitfact (
    workflowstage integer NOT NULL,
    workdoneby character varying(256),
    workdonedate date,
    workcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 225))
)
INHERITS (op);


ALTER TABLE public.workstagevisitfact OWNER TO agrbrdf;

