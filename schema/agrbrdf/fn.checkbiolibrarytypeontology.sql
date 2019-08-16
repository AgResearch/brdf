--
-- Name: checkbiolibrarytypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkbiolibrarytypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.libraryType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'BIOLIBRARY_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid library type ', NEW.libraryType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkbiolibrarytypeontology() OWNER TO agrbrdf;

