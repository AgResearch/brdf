--
-- Name: geneticexpressionfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticexpressionfact (
    geneticob integer,
    biosequenceob integer,
    expressionmapname character varying(2048),
    expressionmaplocus character varying(128),
    speciesname character varying(256),
    speciestaxid integer,
    expressionamount double precision,
    evidence text,
    evidencepvalue double precision,
    CONSTRAINT "$1" CHECK ((obtypeid = 195))
)
INHERITS (op);


ALTER TABLE public.geneticexpressionfact OWNER TO agrbrdf;

