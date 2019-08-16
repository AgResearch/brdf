--
-- Name: getmicroarrayobservationnumfact(integer, character varying, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getmicroarrayobservationnumfact(integer, character varying, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        observationobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        mymissingvaluetoken ALIAS for $4;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select 
         CASE 
            WHEN trim(attributevalue) is null THEN mymissingvaluetoken
            WHEN length(trim(attributevalue)) = 0 THEN  mymissingvaluetoken
            ELSE trim(attributevalue)
         END 
      from microarrayObservationFact 
      where microarrayObservation = observationobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getmicroarrayobservationnumfact(integer, character varying, character varying, character varying) OWNER TO agrbrdf;

