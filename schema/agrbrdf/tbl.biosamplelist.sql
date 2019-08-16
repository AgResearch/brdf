--
-- Name: biosamplelist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplelist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 102))
)
INHERITS (ob);


ALTER TABLE public.biosamplelist OWNER TO agrbrdf;

