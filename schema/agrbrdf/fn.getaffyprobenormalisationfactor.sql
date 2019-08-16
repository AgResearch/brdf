--
-- Name: getaffyprobenormalisationfactor(integer, integer); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getaffyprobenormalisationfactor(integer, integer) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        geneexpressionstudy ALIAS for $1;
        microarrayspotfact ALIAS for $2;
        species varchar;
        factor varchar;
    BEGIN

        -- first get the species classification
        open factcursor for
        select 
           getBioSequenceFact(p.objectob,'Affy Annotation','Species classification (E=endophyte, R=ryegrass, G=Glomeromycetes, B=bacterial control, U=unknown, Junk=not detectable)' )
        from
           predicatelink p where 
           p.predicate = 'ARRAYSPOT-SEQUENCE' and
           p.subjectob = microarrayspotfact; -- example : 4460195
        fetch factcursor into species;

        if not FOUND then 
           close factcursor;
           return null;
        end if;


        if species = null then
           return null;
        elsif species = 'R' then
           factor := getgeneexpressionstudycharfact(geneexpressionstudy,'Normalisation','Ryegrass Factor'); -- example : 4978342
        elsif species = 'E' then
           factor := getgeneexpressionstudycharfact(geneexpressionstudy,'Normalisation','Endophyte Factor');
        else
           return null;
        end if;


        return factor;
    END;
$_$;


ALTER FUNCTION public.getaffyprobenormalisationfactor(integer, integer) OWNER TO agrbrdf;

