--
-- Name: checkpedigreeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkpedigreeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.relationship and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'PEDIGREE_RELATIONSHIP');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid pedigree relationship ', NEW.relationship;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkpedigreeontology() OWNER TO agrbrdf;

