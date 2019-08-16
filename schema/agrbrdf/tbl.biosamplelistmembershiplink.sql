--
-- Name: biosamplelistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE biosamplelistmembershiplink (
    biosamplelist integer NOT NULL,
    biosampleob integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.biosamplelistmembershiplink OWNER TO agrbrdf;

