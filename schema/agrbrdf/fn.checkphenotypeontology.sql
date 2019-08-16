--
-- Name: checkphenotypeontology(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkphenotypeontology() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        terms RECORD;
    BEGIN
        select into terms  * from ontologytermfact where termname = NEW.phenotypeTerm and 
                       ontologyob = (select obid from ontologyOb where ontologyName = (
                          select phenotypeOntologyName from phenotypeStudy where obid = NEW.phenotypestudy));
        if not FOUND then
           RAISE EXCEPTION '% is not a valid phenotype term ', NEW.phenotypeTerm;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkphenotypeontology() OWNER TO agrbrdf;

