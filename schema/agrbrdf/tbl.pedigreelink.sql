--
-- Name: pedigreelink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE pedigreelink (
    subjectob integer NOT NULL,
    objectob integer NOT NULL,
    relationship character varying(64),
    relationshipcomment character varying(256),
    CONSTRAINT "$1" CHECK ((obtypeid = 335))
)
INHERITS (op);


ALTER TABLE public.pedigreelink OWNER TO agrbrdf;

