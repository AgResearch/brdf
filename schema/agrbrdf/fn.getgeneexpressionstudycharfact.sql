--
-- Name: getgeneexpressionstudycharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getgeneexpressionstudycharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        studyobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from geneExpressionStudyFact 
      where geneExpressionStudy = studyobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getgeneexpressionstudycharfact(integer, character varying, character varying) OWNER TO agrbrdf;

