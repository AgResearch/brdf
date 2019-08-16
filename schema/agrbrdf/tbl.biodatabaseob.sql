--
-- Name: biodatabaseob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biodatabaseob (
    databasename character varying(256),
    databasedescription character varying(2048),
    databasetype character varying(2048),
    databasecomment text,
    CONSTRAINT "$1" CHECK ((obtypeid = 315))
)
INHERITS (ob);


ALTER TABLE public.biodatabaseob OWNER TO agrbrdf;

