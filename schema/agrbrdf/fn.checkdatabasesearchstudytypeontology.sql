--
-- Name: checkdatabasesearchstudytypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkdatabasesearchstudytypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.studyType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'DATABASESEARCHSTUDYTYPE_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid studytype ', NEW.studyType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkdatabasesearchstudytypeontology() OWNER TO agrbrdf;

