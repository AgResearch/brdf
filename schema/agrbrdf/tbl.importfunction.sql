--
-- Name: importfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE importfunction (
    ob integer,
    datasourceob integer NOT NULL,
    importprocedureob integer NOT NULL,
    importerrors text,
    processinginstructions text,
    notificationaddresses text,
    submissionreasons text,
    functioncomment character varying(1024),
    CONSTRAINT "$1" CHECK ((obtypeid = 135))
)
INHERITS (op);


ALTER TABLE public.importfunction OWNER TO agrbrdf;

