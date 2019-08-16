--
-- Name: checkbioprotocoltypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbioprotocoltypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.protocolType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIOPROTOCOL_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid protocol type ', NEW.protocolType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbioprotocoltypeontology() OWNER TO agrbrdf;

