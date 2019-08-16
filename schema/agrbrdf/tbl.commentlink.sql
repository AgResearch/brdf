--
-- Name: commentlink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE commentlink (
    commentob integer NOT NULL,
    ob integer NOT NULL,
    commentdate date DEFAULT now(),
    commentby character varying(256),
    style_bgcolour character varying(64) DEFAULT '#99EE99'::character varying
);


ALTER TABLE public.commentlink OWNER TO agrbrdf;

