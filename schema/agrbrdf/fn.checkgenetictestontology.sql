--
-- Name: checkgenetictestontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgenetictestontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.testType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENETICTEST_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid testtype  ', NEW.testType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgenetictestontology() OWNER TO agrbrdf;

