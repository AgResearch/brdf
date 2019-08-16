--
-- Name: checkaccessontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkaccessontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologyTermFact where termname = NEW.accessType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'ACCESS_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid access type ', NEW.accessType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkaccessontology() OWNER TO agrbrdf;

