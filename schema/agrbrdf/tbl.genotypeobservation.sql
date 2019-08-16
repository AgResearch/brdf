--
-- Name: genotypeobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE genotypeobservation (
    genotypestudy integer,
    genetictestfact integer,
    observationdate date,
    genotypeobserved character varying(256),
    genotypeobserveddescription character varying(1024),
    finalgenotype character varying(256),
    finalgenotypedescription character varying(1024),
    observationcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 300))
)
INHERITS (op);


ALTER TABLE public.genotypeobservation OWNER TO agrbrdf;

