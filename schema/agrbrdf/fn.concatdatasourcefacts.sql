--
-- Name: concatdatasourcefacts(integer, character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION concatdatasourcefacts(integer, character varying, character varying) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare 
      mylist alias for $1;
      mynamespace alias for $2;
      myattributename alias for $3;
      result text;
   begin
      select agg_newline_concat(df.attributevalue) into result 
      from 
      datasourcelistmembershiplink dl join datasourcefact df on
      df.datasourceob = dl.datasourceob
      where
      dl.datasourcelist = mylist;
      return result;
   end;
$_$;


ALTER FUNCTION public.concatdatasourcefacts(integer, character varying, character varying) OWNER TO agrbrdf;

