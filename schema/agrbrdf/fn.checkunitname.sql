--
-- Name: checkunitname(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkunitname() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        units RECORD;
    BEGIN
        if NEW.unitName is not null then
           select into units  * from ontologytermfact where termname = NEW.unitName and 
                          ontologyob = (select obid from ontologyOb where ontologyName = 'UNITS');
           if not FOUND then
              RAISE EXCEPTION '% is not a valid unit name ', NEW.unitName;
           else
              return NEW;
           end if;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkunitname() OWNER TO agrbrdf;

