--
-- Name: oblist; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE oblist (
    listname character varying(256) NOT NULL,
    listtype character varying(128),
    listdefinition text,
    bookmark integer,
    maxmembership integer,
    currentmembership integer DEFAULT 0,
    listcomment character varying(1024),
    displayurl character varying(2048) DEFAULT 'ob.gif'::character varying,
    membershipvisibility character varying(32) DEFAULT 'public'::character varying,
    CONSTRAINT "$1" CHECK ((obtypeid = 20))
)
INHERITS (ob);


ALTER TABLE public.oblist OWNER TO agrbrdf;

