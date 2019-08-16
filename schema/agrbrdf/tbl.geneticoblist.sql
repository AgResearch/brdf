--
-- Name: geneticoblist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticoblist (
    listname character varying(256) NOT NULL,
    maxmembership integer,
    listcomment character varying(1024),
    listtype character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 165))
)
INHERITS (ob);


ALTER TABLE public.geneticoblist OWNER TO agrbrdf;

