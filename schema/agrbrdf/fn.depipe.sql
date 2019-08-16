--
-- Name: depipe(character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION depipe(character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   instring alias for $1;
begin
   return lasttoken(instring,'|');
end;$_$;


ALTER FUNCTION public.depipe(character varying) OWNER TO agrbrdf;

