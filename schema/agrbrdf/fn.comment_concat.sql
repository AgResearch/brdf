--
-- Name: comment_concat(text, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION comment_concat(text, text) RETURNS text
    LANGUAGE plpgsql
    AS $_$
   declare
      arg1 alias for $1;
      arg2 alias for $2;
   begin
      return arg1||'
====================Begin Comment====================
'||arg2 || '
====================End Comment====================
';
   end;
$_$;


ALTER FUNCTION public.comment_concat(text, text) OWNER TO agrbrdf;

