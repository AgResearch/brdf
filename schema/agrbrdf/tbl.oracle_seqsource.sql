--
-- Name: oracle_seqsource; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE oracle_seqsource (
    sourcecode character varying(40),
    organismname character varying(40),
    animalname character varying(90),
    sex character varying(10),
    organ character varying(70),
    tissue character varying(290),
    age character varying(100),
    primerdna integer,
    primerpcr integer,
    description character varying(500),
    altlibnum integer,
    organismcode character varying(20),
    breed character varying(50),
    strategydescription character varying(90),
    taxonid integer,
    genotype character varying(10),
    phenotype integer,
    kingdom character varying(10),
    secondspeciestaxid integer,
    strain integer,
    cultivar character varying(10),
    variety integer,
    sequencetype character varying(10),
    sequencesubtype character varying(10),
    expectedsize integer,
    access_flag integer,
    projectid integer,
    preparation_protocol character varying(130),
    fvector_name character varying(20),
    fvector_dbxref integer,
    rvector_name character varying(20),
    rvector_dbxref integer,
    libprepdate character varying(30),
    libpreparedby character varying(20),
    datasubmittedby character varying(10),
    growth_culture_age integer,
    growth_medium integer,
    growth_conditions integer,
    vector_supplier character varying(20),
    restriction_enzymes character varying(10),
    inserts_size character varying(20),
    host_strain character varying(10),
    amplified integer,
    labbook_owner character varying(20),
    labbook_ref character varying(30),
    labbook_pages character varying(10),
    projectcodeid integer,
    seqdbid integer,
    datasourceob integer,
    voptypeid integer
);


ALTER TABLE public.oracle_seqsource OWNER TO agrbrdf;

