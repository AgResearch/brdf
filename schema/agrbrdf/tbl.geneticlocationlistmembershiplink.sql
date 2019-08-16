--
-- Name: geneticlocationlistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneticlocationlistmembershiplink (
    geneticlocationlist integer NOT NULL,
    geneticlocationfact integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.geneticlocationlistmembershiplink OWNER TO agrbrdf;

