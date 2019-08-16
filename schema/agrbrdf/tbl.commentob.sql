--
-- Name: commentob; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE commentob (
    commentstring text NOT NULL,
    commenttype character varying(1024),
    visibility character varying(32) DEFAULT 'public'::character varying,
    commentedob integer,
    voptypeid integer,
    CONSTRAINT "$1" CHECK ((obtypeid = 40))
)
INHERITS (ob);


ALTER TABLE public.commentob OWNER TO agrbrdf;

