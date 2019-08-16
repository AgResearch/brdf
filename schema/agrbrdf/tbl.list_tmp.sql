--
-- Name: list_tmp; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE list_tmp (
    contig_name character varying(30)
);


ALTER TABLE public.list_tmp OWNER TO agrbrdf;

--
-- Name: listorderseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE listorderseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.listorderseq OWNER TO agrbrdf;

--
-- Name: lmf_factidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE lmf_factidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.lmf_factidseq OWNER TO agrbrdf;

