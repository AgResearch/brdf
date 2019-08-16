--
-- Name: workflowmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE workflowmembershiplink (
    workflowob integer NOT NULL,
    workflowstageob integer NOT NULL,
    membershipcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 215))
)
INHERITS (op);


ALTER TABLE public.workflowmembershiplink OWNER TO agrbrdf;

