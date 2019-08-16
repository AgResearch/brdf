--
-- Name: obtype; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE obtype (
    obtypeid integer DEFAULT nextval(('obtype_obtypeidseq'::text)::regclass) NOT NULL,
    displayname character varying(2048),
    uri character varying(2048),
    displayurl character varying(2048) DEFAULT 'ob.gif'::character varying,
    tablename character varying(128),
    namedinstances boolean DEFAULT true,
    isop boolean DEFAULT false,
    isvirtual boolean DEFAULT false,
    isdynamic boolean DEFAULT false,
    owner character varying(128) DEFAULT 'core'::character varying,
    obtypedescription character varying(2048)
);


ALTER TABLE public.obtype OWNER TO agrbrdf;

--
-- Name: TABLE obtype; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON TABLE obtype IS 'Types of object and relation stored in the brdf schema ';


--
-- Name: COLUMN obtype.tablename; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.tablename IS 'Unary relations are called facts, stored in tables named *fact ; binary relations are called links, 
stored in tables named *link ; ternary and higher relations are called either functions or studies and are stored in tables called
*function, or *study ';


--
-- Name: COLUMN obtype.namedinstances; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.namedinstances IS 'Most objects and relations are stored in tables that inherit from the ob table, and hence 
each instance is assigned a unique numeric name (obid) - namedinstances is TRUE for these. Some relations are stored 
in tables that do not inherit from the ob table, and do not have obids - namedInstances is FALSE for these.';


--
-- Name: COLUMN obtype.isop; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.isop IS 'Database entities are either primary objects such as sequences,samples, genes (obs), or 
relations (operations, or ops) between primary objects - e.g. op1(ob1,ob2,ob3...). Obs and ops may also be interpreted 
as nodes and edges in a hypergraph. isop is TRUE for ops or FALSE for obs';


--
-- Name: COLUMN obtype.isvirtual; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.isvirtual IS 'In most cases there is one database table for each type. Some types share a table - these are 
virtual types. is virtual is FALSE for most types, TRUE for types that share a table with another primary type';


--
-- Name: COLUMN obtype.isdynamic; Type: COMMENT; Schema: public; Owner: agrbrdf
--

COMMENT ON COLUMN obtype.isdynamic IS 'In most cases there is one database table for each type. However some types are not stored in a 
database table  but are constructed dynamically at run time';


--
-- Name: obtype_obtypeidseq; Type: SEQUENCE; Schema: public; Owner: agrbrdf
--

CREATE SEQUENCE obtype_obtypeidseq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.obtype_obtypeidseq OWNER TO agrbrdf;

