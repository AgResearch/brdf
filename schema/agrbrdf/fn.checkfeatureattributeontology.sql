--
-- Name: checkfeatureattributeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkfeatureattributeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.attributeName and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'SEQUENCE_FEATURE_ATTRIBUTE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid feature attribute name ', NEW.attributeName;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkfeatureattributeontology() OWNER TO agrbrdf;

