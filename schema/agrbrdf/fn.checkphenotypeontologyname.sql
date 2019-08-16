--
-- Name: checkphenotypeontologyname(); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION checkphenotypeontologyname() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        names RECORD;
    BEGIN
        select into names  * from ontologyOb where ontologyName = NEW.phenotypeOntologyName;
        if not FOUND then
           RAISE EXCEPTION '% is not a valid phenotype ontology ', NEW.phenotypeOntologyName;
        else
           return NEW;
        end if;
    END;
$$;


ALTER FUNCTION public.checkphenotypeontologyname() OWNER TO agrbrdf;

