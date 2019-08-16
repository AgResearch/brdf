--
-- Name: datasourcelistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE datasourcelistmembershiplink (
    datasourcelist integer NOT NULL,
    datasourceob integer NOT NULL,
    inclusioncomment character varying(64),
    listorder integer,
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.datasourcelistmembershiplink OWNER TO agrbrdf;

