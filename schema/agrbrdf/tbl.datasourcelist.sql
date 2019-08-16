--
-- Name: datasourcelist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourcelist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    CONSTRAINT datasourcelist_obtypeid_check CHECK ((obtypeid = 550))
)
INHERITS (ob);


ALTER TABLE public.datasourcelist OWNER TO agrbrdf;

