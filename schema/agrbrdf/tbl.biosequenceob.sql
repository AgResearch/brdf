--
-- Name: biosequenceob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosequenceob (
    sequencename character varying(1024),
    sequencetype character varying(256),
    seqstring text,
    sequencedescription text,
    sequencetopology character varying(32) DEFAULT 'linear'::character varying,
    seqlength integer,
    sequenceurl character varying(2048),
    seqcomment character varying(2048),
    gi integer,
    fnindex_accession character varying(2048),
    fnindex_id character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 115)),
    CONSTRAINT "$2" CHECK ((((sequencetopology)::text = ('linear'::character varying)::text) OR ((sequencetopology)::text = ('circular'::character varying)::text)))
)
INHERITS (ob);


ALTER TABLE public.biosequenceob OWNER TO agrbrdf;

