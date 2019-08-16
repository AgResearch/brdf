--
-- Name: generegulationlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE generegulationlink (
    geneticob integer NOT NULL,
    biosequenceob integer NOT NULL,
    regulationtype character varying(1024),
    evidence text,
    regulationcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 202))
)
INHERITS (op);


ALTER TABLE public.generegulationlink OWNER TO agrbrdf;

