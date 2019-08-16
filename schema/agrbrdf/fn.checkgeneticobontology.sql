--
-- Name: checkgeneticobontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgeneticobontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.geneticObType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENETICOB_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid genetic ob type ', NEW.geneticObType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgeneticobontology() OWNER TO agrbrdf;

