--
-- Name: microarrayspotfact; Type: TABLE; Schema: public; Owner: agrbrdf; Tablespace: 
--

CREATE TABLE microarrayspotfact (
    labresourceob integer NOT NULL,
    accession character varying(256),
    blocknumber integer,
    blockrow integer,
    blockcolumn integer,
    metarow integer,
    metacolumn integer,
    spotcomment character varying(2048),
    gal_block integer,
    gal_column integer,
    gal_row integer,
    gal_name character varying(256),
    gal_id character varying(128),
    gal_refnumber integer,
    gal_controltype character varying(32),
    gal_genename character varying(128),
    gal_tophit character varying(256),
    gal_description character varying(2048),
    CONSTRAINT "$1" CHECK ((obtypeid = 235))
)
INHERITS (op);


ALTER TABLE public.microarrayspotfact OWNER TO agrbrdf;

