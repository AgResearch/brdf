--
-- Name: getdatasourcecharfact(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION getdatasourcecharfact(integer, character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
    DECLARE
        factcursor refcursor;
        datasourceobid ALIAS for $1;
        myfactnamespace ALIAS for $2;
        myattributename ALIAS for $3;
        myattributevalue varchar;
    BEGIN
      open factcursor for
      select trim(attributevalue) from datasourcefact 
      where datasourceob = datasourceobid and   
      factnamespace = myfactnamespace and 
      attributename = myattributename;

      fetch factcursor into myattributevalue;
      close factcursor;
      return myattributevalue;
    END;
$_$;


ALTER FUNCTION public.getdatasourcecharfact(integer, character varying, character varying) OWNER TO agrbrdf;

