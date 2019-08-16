--
-- Name: listmembershipfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE listmembershipfact (
    factid integer DEFAULT nextval('lmf_factidseq'::regclass) NOT NULL,
    oblist integer NOT NULL,
    memberid character varying(2048),
    listorder integer DEFAULT nextval('listorderseq'::regclass),
    createddate date DEFAULT now(),
    createdby character varying(256),
    membershipcomment text,
    voptypeid integer
);


ALTER TABLE public.listmembershipfact OWNER TO agrbrdf;

