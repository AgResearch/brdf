--
-- Name: microarrayfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayfact (
    labresourceob integer NOT NULL,
    arrayname character varying(256),
    arraycomment character varying(2048),
    gal_type character varying(256),
    gal_blockcount integer,
    gal_blocktype integer,
    gal_url character varying(512),
    gal_supplier character varying(512),
    gal_block1 character varying(512),
    CONSTRAINT microarrayfact_gal_block1 CHECK ((obtypeid = 230))
)
INHERITS (op);


ALTER TABLE public.microarrayfact OWNER TO agrbrdf;

