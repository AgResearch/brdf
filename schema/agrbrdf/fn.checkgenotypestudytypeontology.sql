--
-- Name: checkgenotypestudytypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkgenotypestudytypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.studyType and 
                       ontologyob = (select obid from ontologyOb where ontologyName = 'GENOTYPESTUDY_ONTOLOGY');
        if not FOUND then
           RAISE EXCEPTION '% is not a valid studytype term ', NEW.studyType;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkgenotypestudytypeontology() OWNER TO agrbrdf;

