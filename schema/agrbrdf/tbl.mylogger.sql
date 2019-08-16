--
-- Name: mylogger; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE mylogger (
    msgorder integer,
    msgtext text
);


ALTER TABLE public.mylogger OWNER TO agrbrdf;

--
-- Name: ob_obidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE ob_obidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ob_obidseq OWNER TO agrbrdf;

