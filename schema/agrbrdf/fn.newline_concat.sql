--
-- Name: newline_concat(text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION newline_concat(text, text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare
      arg1 alias for $1;
      arg2 alias for $2;
   begin
      if length(arg1) > 0 then
         return arg1||'
'||arg2 ;
      else
         return arg1||arg2 ;
      end if;
   end;
$_$;


ALTER FUNCTION public.newline_concat(text, text) OWNER TO agrbrdf;

