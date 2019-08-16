--
-- Name: mylog(integer, text); Type: FUNCTION; Schema: public; Owner: agrbrdf
--

CREATE FUNCTION mylog(integer, text) RETURNS integer
    LANGUAGE plpgsql
    AS $_$
declare
   argorder alias for $1;
   argtext alias for $2;
begin
   insert into mylogger(msgorder,msgtext) 
   values(argorder,argtext);
   return 0;
end;
$_$;


ALTER FUNCTION public.mylog(integer, text) OWNER TO agrbrdf;

