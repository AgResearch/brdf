--
-- Name: checkanalysistypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkanalysistypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.procedureType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'ANALYSIS_PROCEDURE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid analysis procedure type ', NEW.procedureType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkanalysistypeontology() OWNER TO agrbrdf;

