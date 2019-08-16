--
-- Name: lasttoken(character varying, character varying); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION lasttoken(character varying, character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $_$
declare
   instring alias for $1;
   separator alias for $2;
   sepcount int4;
   ltoken varchar;
   rtoken varchar;
   tokenresult varchar;
begin
   tokenresult := instring;

   -- get how may separators there are 
   sepcount = length(instring) - length(replace(instring,separator,''));

   if sepcount >= 1 then
      ltoken = rtrim(ltrim(split_part(instring,separator,sepcount)));
      rtoken = rtrim(ltrim(split_part(instring,separator,sepcount + 1)));

      tokenresult := rtoken;

      if length(rtoken) = 0 then
         tokenresult := ltoken;
      end if;
   end if;
   
   return tokenresult;
end;$_$;


ALTER FUNCTION public.lasttoken(character varying, character varying) OWNER TO agrbrdf;

