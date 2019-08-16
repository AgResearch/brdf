--
-- Name: sequencealignmentfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE sequencealignmentfact (
    databasesearchobservation integer NOT NULL,
    bitscore double precision,
    score double precision,
    evalue double precision,
    queryfrom numeric(12,0),
    queryto numeric(12,0),
    hitfrom numeric(12,0),
    hitto numeric(12,0),
    queryframe integer,
    hitframe integer,
    identities integer,
    positives integer,
    alignlen integer,
    hspqseq text,
    hsphseq text,
    hspmidline text,
    alignmentcomment character varying(2048),
    hitstrand integer,
    gaps integer,
    mismatches integer,
    pctidentity double precision,
    indels integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 330))
)
INHERITS (op);


ALTER TABLE public.sequencealignmentfact OWNER TO agrbrdf;

