--
-- Name: geneproductlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneproductlink (
    geneticob integer NOT NULL,
    biosequenceob integer NOT NULL,
    producttype character varying(1024),
    evidence text,
    productcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 201))
)
INHERITS (op);


ALTER TABLE public.geneproductlink OWNER TO agrbrdf;

