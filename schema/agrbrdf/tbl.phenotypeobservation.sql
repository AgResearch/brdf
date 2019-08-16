--
-- Name: phenotypeobservation; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE phenotypeobservation (
    biosampleob integer,
    biosamplelist integer,
    biosubjectob integer,
    phenotypestudy integer NOT NULL,
    phenotypenamespace character varying(1024),
    phenotypeterm character varying(2048),
    phenotyperawscore double precision,
    phenotypeadjustedscore double precision,
    observationcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 155))
)
INHERITS (op);


ALTER TABLE public.phenotypeobservation OWNER TO agrbrdf;

