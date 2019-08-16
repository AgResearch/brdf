--
-- Name: biosequencefeaturefact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosequencefeaturefact (
    biosequenceob integer NOT NULL,
    featuretype character varying(256),
    featureaccession character varying(256),
    featurestart integer,
    featurestop integer,
    featurestrand integer,
    featurecomment text,
    evidence text,
    featurelength integer,
    score double precision,
    CONSTRAINT "$1" CHECK ((obtypeid = 117))
)
INHERITS (op);


ALTER TABLE public.biosequencefeaturefact OWNER TO agrbrdf;

