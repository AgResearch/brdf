--
-- Name: geneticoblistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticoblistmembershiplink (
    geneticoblist integer NOT NULL,
    geneticob integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.geneticoblistmembershiplink OWNER TO agrbrdf;

