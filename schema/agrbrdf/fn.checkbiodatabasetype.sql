--
-- Name: checkbiodatabasetype(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbiodatabasetype() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.databaseType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIODATABASETYPE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid biodatabase type ', NEW.databaseType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbiodatabasetype() OWNER TO agrbrdf;

