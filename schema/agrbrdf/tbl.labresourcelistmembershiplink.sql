--
-- Name: labresourcelistmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE labresourcelistmembershiplink (
    labresourcelist integer NOT NULL,
    labresourceob integer NOT NULL,
    inclusioncomment character varying(64),
    addeddate date DEFAULT now(),
    addedby character varying(256)
);


ALTER TABLE public.labresourcelistmembershiplink OWNER TO agrbrdf;

