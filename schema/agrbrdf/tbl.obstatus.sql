--
-- Name: obstatus; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE obstatus (
    statuscode integer NOT NULL,
    statusname character varying(128) NOT NULL,
    statusdescription character varying(2048)
);


ALTER TABLE public.obstatus OWNER TO agrbrdf;

--
-- Name: TABLE obstatus; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON TABLE obstatus IS 'This table will be used to support object versioning, with previous versions having inactive 	status and 	linked to current versions via a link table';


