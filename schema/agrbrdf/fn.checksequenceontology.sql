--
-- Name: checksequenceontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checksequenceontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.sequenceType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'AGSEQUENCE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid sequence type ', NEW.sequenceType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checksequenceontology() OWNER TO agrbrdf;

