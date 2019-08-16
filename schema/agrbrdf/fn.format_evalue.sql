--
-- Name: format_evalue(double precision); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION format_evalue(double precision) RETURNS character varying
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $_$
declare
   evalue alias for $1;
   mantissa double precision;
   exponent integer;
   strevalue varchar;
begin
   strevalue := '';
   if evalue = 0.0 then
      strevalue := '0.0';
   else 
      exponent := round(log(evalue));
      mantissa := evalue/power(10,exponent);
      strevalue := to_char(mantissa,'999.999') || 'e' || rtrim(ltrim(to_char(exponent,'99999')));
   end if;

   return strevalue;
end
$_$;


ALTER FUNCTION public.format_evalue(double precision) OWNER TO agrbrdf;

