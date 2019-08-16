--
-- Name: workflowlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowlink (
    fromstage integer NOT NULL,
    tostage integer NOT NULL,
    workcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 220))
)
INHERITS (op);


ALTER TABLE public.workflowlink OWNER TO agrbrdf;

