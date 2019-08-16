--
-- Name: uriob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE uriob (
    uristring character varying(2048) NOT NULL,
    uritype character varying(256),
    uricomment character varying(1024),
    visibility character varying(32) DEFAULT 'public'::character varying,
    CONSTRAINT "$1" CHECK ((obtypeid = 30))
)
INHERITS (ob);


ALTER TABLE public.uriob OWNER TO agrbrdf;

