--
-- Name: SEQSOURCE; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE "SEQSOURCE" (
    "SOURCECODE" character varying(50),
    "ORGANISMNAME" character varying(100),
    "ANIMALNAME" character varying(100),
    "SEX" character varying(16),
    "ORGAN" character varying(100),
    "TISSUE" character varying(2000),
    "AGE" character varying(100),
    "PRIMERDNA" double precision,
    "PRIMERPCR" double precision,
    "DESCRIPTION" character varying(1000),
    "ALTLIBNUM" double precision,
    "ORGANISMCODE" character varying(64),
    "BREED" character varying(128),
    "STRATEGYDESCRIPTION" character varying(2000),
    "TAXONID" double precision,
    "GENOTYPE" character varying(100),
    "PHENOTYPE" character varying(100),
    "KINGDOM" character varying(64),
    "SECONDSPECIESTAXID" double precision,
    "STRAIN" character varying(64),
    "CULTIVAR" character varying(64),
    "VARIETY" character varying(64),
    "SEQUENCETYPE" character varying(64),
    "SEQUENCESUBTYPE" character varying(64),
    "EXPECTEDSIZE" double precision,
    "ACCESS_FLAG" double precision,
    "PROJECTID" double precision,
    "PREPARATION_PROTOCOL" character varying(4000),
    "FVECTOR_NAME" character varying(64),
    "FVECTOR_DBXREF" character varying(64),
    "RVECTOR_NAME" character varying(64),
    "RVECTOR_DBXREF" character varying(64),
    "LIBPREPDATE" timestamp(0) without time zone,
    "LIBPREPAREDBY" character varying(64),
    "DATASUBMITTEDBY" character varying(64),
    "GROWTH_CULTURE_AGE" double precision,
    "GROWTH_MEDIUM" character varying(64),
    "GROWTH_CONDITIONS" character varying(4000),
    "VECTOR_SUPPLIER" character varying(64),
    "RESTRICTION_ENZYMES" character varying(4000),
    "INSERTS_SIZE" character varying(64),
    "HOST_STRAIN" character varying(64),
    "AMPLIFIED" double precision,
    "LABBOOK_OWNER" character varying(64),
    "LABBOOK_REF" character varying(64),
    "LABBOOK_PAGES" character varying(64),
    "PROJECTCODEID" double precision,
    "SEQDBID" double precision
);


ALTER TABLE public."SEQSOURCE" OWNER TO agrbrdf;

