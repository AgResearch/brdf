--
-- Name: checkgeneticlistontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgeneticlistontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.listType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENETIC_LIST_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid genetic list type ', NEW.listType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgeneticlistontology() OWNER TO agrbrdf;

