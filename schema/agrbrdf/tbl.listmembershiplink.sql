--
-- Name: listmembershiplink; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE listmembershiplink (
    oblist integer NOT NULL,
    ob integer NOT NULL,
    obxreflsid character varying(2048),
    listorder integer DEFAULT nextval(('listorderseq'::text)::regclass),
    createddate date DEFAULT now(),
    createdby character varying(256),
    membershipcomment text,
    voptypeid integer
);


ALTER TABLE public.listmembershiplink OWNER TO agrbrdf;

