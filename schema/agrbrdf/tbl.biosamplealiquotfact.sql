--
-- Name: biosamplealiquotfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplealiquotfact (
    biosampleob integer NOT NULL,
    aliquotvolume double precision,
    aliquotvolumeunit character varying(64),
    aliquotcount double precision,
    aliquotcountunit character varying(64),
    aliquotweight double precision,
    aliquotweightunit character varying(64),
    aliquotdme double precision,
    aliquotdmeunit character varying(64),
    aliquottype character varying(64),
    aliquotdate date,
    aliquotcomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 400))
)
INHERITS (op);


ALTER TABLE public.biosamplealiquotfact OWNER TO agrbrdf;

