--
-- Name: urilink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE urilink (
    uriob integer NOT NULL,
    ob integer NOT NULL,
    displaystring character varying(2048),
    displayorder integer,
    iconpath character varying(512),
    iconattributes character varying(2048),
    createddate date DEFAULT now(),
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256),
    uricomment character varying(256),
    linktype character varying(256)
);


ALTER TABLE public.urilink OWNER TO agrbrdf;

