--
-- Name: staffob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE staffob (
    loginname character varying(64) NOT NULL,
    fullname character varying(128),
    emailaddress character varying(256),
    mobile character varying(64),
    phone character varying(64),
    title character varying(32),
    staffcomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 50))
)
INHERITS (ob);


ALTER TABLE public.staffob OWNER TO agrbrdf;

