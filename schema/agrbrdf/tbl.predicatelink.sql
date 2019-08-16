--
-- Name: predicatelink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE predicatelink (
    subjectob integer NOT NULL,
    objectob integer NOT NULL,
    predicate character varying(64),
    predicatecomment character varying(256),
    CONSTRAINT "$1" CHECK ((obtypeid = 15))
)
INHERITS (op);


ALTER TABLE public.predicatelink OWNER TO agrbrdf;

