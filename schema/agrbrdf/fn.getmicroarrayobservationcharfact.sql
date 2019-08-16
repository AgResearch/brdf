--
-- Name: getmicroarrayobservationcharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getmicroarrayobservationcharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        observationobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from microarrayObservationFact 
      where microarrayObservation = observationobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getmicroarrayobservationcharfact(integer, character varying, character varying) OWNER TO agrbrdf;

