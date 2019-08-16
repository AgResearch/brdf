--
-- Name: geneticlocationfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticlocationfact (
    geneticob integer,
    biosequenceob integer,
    genetictestfact integer,
    mapname character varying(2048),
    maptype character varying(2048) DEFAULT 'sequence'::character varying,
    mapunit character varying(128) DEFAULT 'bases'::character varying,
    speciesname character varying(256),
    speciestaxid integer,
    entrezgeneid integer,
    locusname character varying(256),
    locustag character varying(128),
    locussynonyms character varying(2048),
    chromosomename0 character varying(32),
    strand character varying(3),
    locationstart numeric(12,0),
    locationstop numeric(12,0),
    locationstring character varying(2048),
    regionsize numeric(12,0),
    markers character varying(2048),
    locationdescription character varying(2048),
    othermaplocation1 character varying(128),
    evidence text,
    evidencescore double precision,
    evidencepvalue double precision,
    chromosomename character varying(128),
    mapobid integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 175)),
    CONSTRAINT "$2" CHECK ((((((maptype)::text = ('linkage'::character varying)::text) OR ((maptype)::text = ('rh'::character varying)::text)) OR ((maptype)::text = ('sequence'::character varying)::text)) OR ((maptype)::text = ('physical'::character varying)::text))),
    CONSTRAINT "$3" CHECK ((((mapunit)::text = ('centiMorgans'::character varying)::text) OR ((mapunit)::text = ('bases'::character varying)::text)))
)
INHERITS (op);


ALTER TABLE public.geneticlocationfact OWNER TO agrbrdf;

