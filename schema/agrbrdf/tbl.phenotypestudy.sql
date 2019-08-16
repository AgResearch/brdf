--
-- Name: phenotypestudy; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE phenotypestudy (
    studyname character varying(1024) NOT NULL,
    phenotypeontologyname character varying(256) DEFAULT 'MYPHENOTYPE'::character varying,
    studydescription text,
    studydate date,
    CONSTRAINT "$1" CHECK ((obtypeid = 150))
)
INHERITS (ob);


ALTER TABLE public.phenotypestudy OWNER TO agrbrdf;

