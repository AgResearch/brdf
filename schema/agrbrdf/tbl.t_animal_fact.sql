--
-- Name: t_animal_fact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE t_animal_fact (
    animalid integer,
    labid character varying(20),
    stud character varying(20),
    yob integer,
    uidtag character varying(60),
    sex character varying(10),
    species character varying(20),
    damid integer,
    sireid integer,
    ownerid integer,
    breed character varying(40),
    family character varying(10),
    sil_ignore character varying(10),
    sil_reconciled character varying(10),
    sil_requery character varying(10),
    sil_sex character varying(20),
    sil_status character varying(20),
    comment character varying(230),
    birthdate character varying(20),
    sys_created character varying(30),
    sys_createdby character varying(20),
    ovitacontractnumber character varying(40),
    sil_tag character varying(20),
    sil_flock_code integer,
    sil_reconciled_date character varying(30),
    biosubjectob integer NOT NULL
);


ALTER TABLE public.t_animal_fact OWNER TO agrbrdf;

