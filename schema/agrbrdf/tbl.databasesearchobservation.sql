--
-- Name: databasesearchobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE databasesearchobservation (
    databasesearchstudy integer NOT NULL,
    querysequence integer NOT NULL,
    hitsequence integer NOT NULL,
    queryxreflsid character varying(2048),
    querylength numeric(12,0),
    hitxreflsid character varying(2048),
    hitdescription text,
    hitlength numeric(12,0),
    hitevalue double precision,
    hitpvalue double precision,
    rawsearchresult text,
    observationcomment character varying(2048),
    userflags character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 325))
)
INHERITS (op);


ALTER TABLE public.databasesearchobservation OWNER TO agrbrdf;

