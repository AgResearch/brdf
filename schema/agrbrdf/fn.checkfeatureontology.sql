--
-- Name: checkfeatureontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkfeatureontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.featureType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'SEQUENCE_FEATURE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid feature name ', NEW.featureType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkfeatureontology() OWNER TO agrbrdf;

