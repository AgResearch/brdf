--
-- Name: geneexpressionstudy_backup01032009; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE geneexpressionstudy_backup01032009 (
    obid integer,
    obtypeid integer,
    xreflsid character varying(2048),
    createddate date,
    createdby character varying(256),
    lastupdateddate date,
    lastupdatedby character varying(256),
    checkedout boolean,
    checkedoutby character varying(256),
    checkoutdate date,
    obkeywords character varying(4096),
    statuscode integer,
    voptypeid integer,
    biosamplelist integer,
    labresourcelist integer,
    labresourceob integer,
    bioprotocolob integer,
    studytype character varying(128),
    studydescription text,
    studyname character varying(128)
);


ALTER TABLE public.geneexpressionstudy_backup01032009 OWNER TO agrbrdf;

