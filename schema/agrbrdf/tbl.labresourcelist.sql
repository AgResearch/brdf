--
-- Name: labresourcelist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE labresourcelist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 75))
)
INHERITS (ob);


ALTER TABLE public.labresourcelist OWNER TO agrbrdf;

