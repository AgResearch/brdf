--
-- Name: checkbiosampletypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbiosampletypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.sampleType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIOSAMPLE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid sample type ', NEW.sampleType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbiosampletypeontology() OWNER TO agrbrdf;

