--
-- Name: labresourceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE labresourceob (
    resourcename character varying(1024),
    resourcetype character varying(256) NOT NULL,
    resourcesequence text,
    forwardprimersequence text,
    reverseprimersequence text,
    resourceseqlength integer,
    resourcedate date,
    resourcedescription text,
    supplier character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 70))
)
INHERITS (ob);


ALTER TABLE public.labresourceob OWNER TO agrbrdf;

