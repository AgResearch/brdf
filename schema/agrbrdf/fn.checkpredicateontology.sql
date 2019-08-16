--
-- Name: checkpredicateontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkpredicateontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.predicate and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'PREDICATE_TYPES');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid predicate type ', NEW.predicate;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkpredicateontology() OWNER TO agrbrdf;

