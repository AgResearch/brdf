--
-- Name: literaturereferencelink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE literaturereferencelink (
    ob integer NOT NULL,
    literaturereferenceob integer NOT NULL,
    linkcomment text
);


ALTER TABLE public.literaturereferencelink OWNER TO agrbrdf;

