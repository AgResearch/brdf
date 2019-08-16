--
-- Name: biosamplingfunction; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplingfunction (
    biosubjectob integer NOT NULL,
    biosampleob integer NOT NULL,
    bioprotocolob integer,
    labresourcelist integer,
    labresourceob integer,
    labbookreference character varying(2048),
    samplingcomment character varying(1024),
    samplingdate date,
    CONSTRAINT "$1" CHECK ((obtypeid = 100))
)
INHERITS (op);


ALTER TABLE public.biosamplingfunction OWNER TO agrbrdf;

