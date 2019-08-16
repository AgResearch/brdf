--
-- Name: checklabresourceontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checklabresourceontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.resourceType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'LABRESOURCE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid lab resource type ', NEW.resourceType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checklabresourceontology() OWNER TO agrbrdf;

