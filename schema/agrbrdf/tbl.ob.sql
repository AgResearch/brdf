--
-- Name: ob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE ob (
    obid integer DEFAULT nextval(('ob_obidseq'::text)::regclass) NOT NULL,
    obtypeid integer DEFAULT 0 NOT NULL,
    xreflsid character varying(2048) NOT NULL,
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256),
    checkedout boolean DEFAULT false,
    checkedoutby character varying(256),
    checkoutdate date,
    obkeywords character varying(4096),
    statuscode integer DEFAULT 1
);


ALTER TABLE public.ob OWNER TO agrbrdf;

--
-- Name: TABLE ob; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON TABLE ob IS 'Most objects and relations are stored in tables that inherit from the ob table, and hence 
each instance is assigned a unique numeric name (obid)';


--
-- Name: COLUMN ob.obid; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN ob.obid IS 'obid is the principal internal unique identifier for each object. Note that obid is not portable - e.g. on 
import of the data to a new instance, obid may be different. obid is distinct from the postgres OID';


--
-- Name: COLUMN ob.xreflsid; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN ob.xreflsid IS 'This is a pseudo lsid (life sciences identifier), for each object - a human readable unique name. Note that
the xreflsid is not in fact guaranteed to be unique, and would need to be processed by an lsid filter before being published as a true lsid';


